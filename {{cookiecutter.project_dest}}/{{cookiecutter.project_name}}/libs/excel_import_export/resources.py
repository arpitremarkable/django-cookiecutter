import logging
import traceback
from copy import deepcopy

from django.db.models.query import QuerySet
from django.db.transaction import (
    savepoint, savepoint_commit, savepoint_rollback,
)
from django.utils.encoding import force_text

# third party
import tablib
from import_export import instance_loaders, resources
from import_export.results import RowResult
from import_export.utils import atomic_if_using_transaction
from openpyxl.utils import get_column_interval

from . import fields, utils


logging.getLogger(__name__).addHandler(logging.NullHandler())


class ExcelModelInstanceLoader(instance_loaders.ModelInstanceLoader):

    def get_instance(self, row):
        try:
            params = {}
            for key in self.resource.unique_key_field().fields:
                field = self.resource.fields[key]
                if isinstance(field, fields.ExcelField):
                    fval = field.clean(row, self.resource.resource_map)
                else:
                    fval = field.clean(row)
                if fval:
                    params[field.attribute] = fval
            return self.resource.get_queryset().get(**params) if params else None
        except self.resource._meta.model.DoesNotExist:
            return None


class ExcelMPTTModelInstanceLoader(ExcelModelInstanceLoader):

    def get_instance(self, row):
        try:
            qs = self.get_queryset()

            import_field = self.resource.fields['name']
            parent_field = self.resource.fields['parent']

            parent_val = parent_field.clean(row, self.resource.resource_map)
            if parent_val:
                qs = qs.filter(parent=parent_val)
            import_val = import_field.clean(row)
            return qs.get(**{import_field.attribute: import_val})

        except self.resource._meta.model.DoesNotExist:
            return None


class ExcelGenericModelInstanceLoader(ExcelModelInstanceLoader):

    def get_queryset(self, model_cls):
        return model_cls.all_objects.all()

    def get_instance(self, row):
        content_type_field = self.resource.fields['content_type']
        content_type = content_type_field.clean(row, self.resource.resource_map)
        model_cls = content_type.model_class()

        try:
            params = {}
            for key in self.resource.unique_key_field().fields:
                field = self.resource.fields[key]
                if isinstance(field, fields.ExcelField):
                    fval = field.clean(row, self.resource.resource_map)
                else:
                    fval = field.clean(row)
                if fval:
                    params[field.attribute] = fval
            return content_type.get_object_for_this_type(**params) if params else None
        except model_cls.DoesNotExist:
            return None


class ExcelModelDiff(resources.Diff):

    def __init__(self, resource, instance, new, row_no):
        self.row_no = row_no
        self.left = self._export_resource_fields(resource, instance) if not new else []
        self.right = []
        self.new = new

    def _export_resource_fields(self, resource, instance):
        resource.resource_map[resource.sheet_title]['row_map'][str(instance)] = self.row_no
        return [resource.export_field(f, instance, self.row_no) if instance else "" for f in resource.get_user_visible_fields()]


class ExcelModelResource(resources.ModelResource):

    def __init__(self, resource_map):
        super(ExcelModelResource, self).__init__()
        self.resource_map = resource_map
        self.resource_map[self.sheet_title] = {
            'col_map': {},
            'row_map': {},
        }
        self.set_col_map()

    class Meta:
        instance_loader_class = ExcelModelInstanceLoader

    @property
    def sheet_title(self):
        return utils.get_sheet_title(self._meta.model)

    @classmethod
    def unique_key_field(cls):
        return cls.fields.get('unique_key')

    def set_col_map(self):
        field_list = list(self.get_export_order())
        column_list = get_column_interval(1, len(field_list))
        col_map = dict(zip(field_list, column_list))
        self.resource_map[self.sheet_title]['col_map'] = col_map

    def get_export_order(self):
        order_list = list(super(ExcelModelResource, self).get_export_order())
        order_list.insert(0, order_list.pop(order_list.index('unique_key')))
        return tuple(order_list)

    @classmethod
    def get_diff_class(self):
        """
        Returns the class used to display the diff for an imported instance.
        """
        return ExcelModelDiff

    def import_field(self, field, obj, data, is_m2m=False):
        if field.attribute and field.column_name in data:
            if isinstance(field, fields.ExcelField):
                return field.save(obj, data, is_m2m, res_map=self.resource_map)
            return field.save(obj, data, is_m2m)

    def after_import_instance(self, instance, new, **kwargs):
        self.resource_map[self.sheet_title]['row_map'][kwargs.get('row_no')] = instance

    def import_data_inner(self, dataset, dry_run, raise_errors, using_transactions, collect_failed_rows, **kwargs):
        result = self.get_result_class()()
        result.diff_headers = self.get_diff_headers()
        result.total_rows = len(dataset)

        if using_transactions:
            # when transactions are used we want to create/update/delete object
            # as transaction will be rolled back if dry_run is set
            sp1 = savepoint()

        try:
            with atomic_if_using_transaction(using_transactions):
                self.before_import(dataset, using_transactions, dry_run, **kwargs)
        except Exception as e:
            logging.exception(e)
            tb_info = traceback.format_exc()
            result.append_base_error(self.get_error_result_class()(e, tb_info))
            if raise_errors:
                raise

        instance_loader = self._meta.instance_loader_class(self, dataset)

        # Update the total in case the dataset was altered by before_import()
        result.total_rows = len(dataset)

        if collect_failed_rows:
            result.add_dataset_headers(dataset.headers)

        for idx, row in enumerate(dataset.dict):
            with atomic_if_using_transaction(using_transactions):
                row_result = self.import_row(
                    row,
                    instance_loader,
                    using_transactions=using_transactions,
                    dry_run=dry_run,
                    row_no=str(idx+2),
                    **kwargs
                )
            result.increment_row_result_total(row_result)
            if row_result.errors:
                if collect_failed_rows:
                    result.append_failed_row(row, row_result.errors[0])
                if raise_errors:
                    raise row_result.errors[-1].error
            if (row_result.import_type != RowResult.IMPORT_TYPE_SKIP or
                    self._meta.report_skipped):
                result.append_row_result(row_result)
        try:
            with atomic_if_using_transaction(using_transactions):
                self.after_import(dataset, result, using_transactions, dry_run, **kwargs)
        except Exception as e:
            logging.exception(e)
            tb_info = traceback.format_exc()
            result.append_base_error(self.get_error_result_class()(e, tb_info))
            if raise_errors:
                raise

        if using_transactions:
            if dry_run or result.has_errors():
                savepoint_rollback(sp1)
            else:
                savepoint_commit(sp1)

        return result

    def import_row(self, row, instance_loader, using_transactions=True, dry_run=False, **kwargs):
        """
        Imports data from ``tablib.Dataset``. Refer to :doc:`import_workflow`
        for a more complete description of the whole import process.

        :param row: A ``dict`` of the row to import

        :param instance_loader: The instance loader to be used to load the row

        :param using_transactions: If ``using_transactions`` is set, a transaction
            is being used to wrap the import

        :param dry_run: If ``dry_run`` is set, or error occurs, transaction
            will be rolled back.
        """
        row_result = self.get_row_result_class()()
        # try:
        self.before_import_row(row, **kwargs)
        instance, new = self.get_or_init_instance(instance_loader, row)
        self.after_import_instance(instance, new, **kwargs)
        if new:
            row_result.import_type = RowResult.IMPORT_TYPE_NEW
        else:
            row_result.import_type = RowResult.IMPORT_TYPE_UPDATE
        row_result.new_record = new
        original = deepcopy(instance)
        # diff = self.get_diff_class()(self, original, new, kwargs.get('row_no'))

        if self.for_delete(row, instance):
            if new:
                row_result.import_type = RowResult.IMPORT_TYPE_SKIP
                # diff.compare_with(self, None, dry_run)
            else:
                row_result.import_type = RowResult.IMPORT_TYPE_DELETE
                self.delete_instance(instance, using_transactions, dry_run)
                # diff.compare_with(self, None, dry_run)
        else:
            self.import_obj(instance, row, dry_run)
            if self.skip_row(instance, original):
                row_result.import_type = RowResult.IMPORT_TYPE_SKIP
            else:
                self.save_instance(instance, using_transactions, dry_run)
                self.save_m2m(instance, row, using_transactions, dry_run)
            # diff.compare_with(self, instance, dry_run)
        # row_result.diff = diff.as_html()
        # Add object info to RowResult for LogEntry
        if row_result.import_type != RowResult.IMPORT_TYPE_SKIP:
            row_result.object_id = instance.pk
            row_result.object_repr = force_text(instance)
        self.after_import_row(row, row_result, **kwargs)
        """
        except Exception as e:
            row_result.import_type = RowResult.IMPORT_TYPE_ERROR
            # There is no point logging a transaction error for each row
            # when only the original error is likely to be relevant
            if not isinstance(e, TransactionManagementError):
                logging.exception(e)
            tb_info = traceback.format_exc()
            row_result.errors.append(self.get_error_result_class()(e, tb_info, row))
        """
        return row_result

    def import_obj(self, obj, data, dry_run):
        for field in self.get_import_fields():
            if isinstance(field, fields.ManyToManyField):
                continue
            elif field.column_name == 'id' and obj.id:
                continue
            self.import_field(field, obj, data)

    def save_m2m(self, obj, data, using_transactions, dry_run):
        if not using_transactions and dry_run:
            # we don't have transactions and we want to do a dry_run
            pass
        else:
            for field in self.get_import_fields():
                if not isinstance(field, fields.ManyToManyField):
                    continue
                self.import_field(field, obj, data, True)

    def export_field(self, field, obj, row_no):
        field_name = self.get_field_name(field)
        method = getattr(self, 'dehydrate_%s' % field_name, None)
        if method is not None:
            return method(obj)
        if isinstance(field, fields.ExcelField):
            return field.export(obj, row_no=row_no, res_map=self.resource_map)
        return field.export(obj)

    def export_resource(self, obj, row_no):
        return [self.export_field(field, obj, row_no) for field in self.get_export_fields()]

    @property
    def cell_map(self):
        return self.resource_map.get(self.sheet_title)

    def get_local_address(self, val):
        return self._cell_map.get(val, None)

    def get_absolute_address(self, val):
        return '${sheet_title}!{local_address}'.format(
            sheet_title=self.sheet_title,
            local_address=self.get_local_address(val)
        )

    def export(self, queryset=None, *args, **kwargs):
        """
        Exports a resource.
        """
        self.before_export(queryset, *args, **kwargs)

        if queryset is None:
            queryset = self.get_queryset()
        headers = self.get_export_headers()
        data = tablib.Dataset(headers=headers, title=self.sheet_title)

        if isinstance(queryset, QuerySet):
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for idx, obj in enumerate(iterable):
            data.append(self.export_resource(obj=obj, row_no=idx+2))
            self.resource_map[self.sheet_title]['row_map'][str(obj)] = idx + 2

        self.after_export(queryset, data, *args, **kwargs)

        return data


class ExcelMPTTModelResource(ExcelModelResource):

    class Meta:
        instance_loader_class = ExcelMPTTModelInstanceLoader


class ExcelGenericModelResource(ExcelModelResource):

    class Meta:
        instance_loader_class = ExcelGenericModelInstanceLoader

    def init_instance(self, row=None):
        content_type_field = self.fields['content_type']
        content_type = content_type_field.clean(row, self.resource_map)
        model_cls = content_type.model_class()
        return model_cls()
