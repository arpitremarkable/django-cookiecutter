from __future__ import with_statement

import importlib
from collections import OrderedDict
from datetime import datetime

from django.conf import settings
from django.utils import six

# third party
import tablib
from import_export.tmp_storages import TempFolderStorage

from . import formats as base_formats


SKIP_ADMIN_LOG = getattr(settings, 'IMPORT_EXPORT_SKIP_ADMIN_LOG', False)
TMP_STORAGE_CLASS = getattr(settings, 'IMPORT_EXPORT_TMP_STORAGE_CLASS',
                            TempFolderStorage)
if isinstance(TMP_STORAGE_CLASS, six.string_types):
    try:
        # Nod to tastypie's use of importlib.
        parts = TMP_STORAGE_CLASS.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        TMP_STORAGE_CLASS = getattr(module, class_name)
    except ImportError:
        msg = "Could not import '%s' for import_export setting 'IMPORT_EXPORT_TMP_STORAGE_CLASS'" % TMP_STORAGE_CLASS
        raise ImportError(msg)

#: These are the default formats for import and export. Whether they can be
#: used or not is depending on their implementation in the tablib library.
DEFAULT_FORMATS = (
    base_formats.XLSXBook
)


class WorkbookImportExportMixin(object):
    """
    Import Export mixin.
    """
    #: unique workbook name
    workbook_name = ''
    #: resource class
    resource_classes = []
    formats = DEFAULT_FORMATS
    change_list_template = 'admin/import_export/change_list_export.html'
    #: template for export view
    export_template_name = 'admin/import_export/export.html'
    to_encoding = "utf-8"
    tmp_storage_class = None

    def __init__(self, *args, **kwargs):
        self.resource_map = OrderedDict()
        self.name = self.workbook_name
        self.title_resource_map = self.init_resources()

    @property
    def resources(self):
        return self.title_resource_map.values()

    def init_resources(self):
        title_resource_map = OrderedDict()
        for resource_class in self.get_resource_classes():
            r = resource_class(**self.get_resource_kwargs())
            title_resource_map[r.sheet_title] = r
        return title_resource_map

    def get_resource_classes(self):
        return self.resource_classes

    def get_resource_kwargs(self, *args, **kwargs):
        return {
            'resource_map': self.resource_map
        }

    def get_tmp_storage_class(self):
        if self.tmp_storage_class is None:
            return TMP_STORAGE_CLASS
        else:
            return self.tmp_storage_class

    def get_export_filename(self, file_format):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % (
                self.workbook_name,
                date_str,
                file_format.get_extension()
            )
        return filename

    def get_export_data(self, file_format, *args, **kwargs):
        """
        Returns file_format representation for given queryset.
        """
        book = tablib.Databook()
        for resource in self.resources:
            dataset = resource.export(queryset=None, *args, **kwargs)
            book.add_sheet(dataset)
        export_data = file_format.export_databook(databook=book)
        return export_data

    def import_action(self, import_file, *args, **kwargs):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        input_format = base_formats.XLSXBook()

        # first always write the uploaded file to disk as it may be a
        # memory file or else based on settings upload handlers
        tmp_storage = self.get_tmp_storage_class()()
        data = bytes()
        for chunk in import_file.chunks():
            data += chunk
        tmp_storage.save(data, input_format.get_read_mode())

        # then read the file, using the proper format-specific mode
        # warning, big files may exceed memory
        data = tmp_storage.read(input_format.get_read_mode())
        databook = tablib.Databook()
        input_format.fill_databook(databook, data)
        results = self.run_import(databook)
        tmp_storage.remove()

        return results

    def process_import(self, import_file_name, *args, **kwargs):
        """
        Perform the actual import action (after the user has confirmed the import)
        """
        results = []
        input_format = base_formats.XLSXBook
        tmp_storage = self.get_tmp_storage_class()(name=import_file_name)
        data = tmp_storage.read(input_format.get_read_mode())
        dataset = input_format.create_dataset(data)
        # databook = create databook (data)
        # for dataset in databook.datasets:
        #   resource = self.title_resource_map[dataset.title]
        #   results.append[self.process_dataset(dataset, resource)]
        results.append(self.process_dataset(dataset, *args, **kwargs))
        tmp_storage.remove()
        return self.process_results(results)

    def run_import(self, databook, dry_run):
        results = []
        for i, dataset in enumerate(databook.sheets()):
            try:
                resource = self.title_resource_map[dataset.title]
            except KeyError:
                resource = list(self.title_resource_map.values())[i]
                assert list(self.title_resource_map.keys())[i].startswith(dataset.title), 'probably wrong sheet'
            results.append(
                resource.import_data(dataset, dry_run=dry_run, raise_errors=False)
            )
        return results

    def process_dataset(self, dataset, resource, *args, **kwargs):
        return resource.import_data(dataset,
                                    dry_run=False,
                                    raise_errors=True,
                                    *args,
                                    **kwargs)

    def process_results(self, results, request):
        for result in results:
            self.generate_log_entries(result, request)

    def generate_log_entries(self, result,):
        pass
        """
        if not self.get_skip_admin_log():
            # Add imported objects to LogEntry
            logentry_map = {
                RowResult.IMPORT_TYPE_NEW: ADDITION,
                RowResult.IMPORT_TYPE_UPDATE: CHANGE,
                RowResult.IMPORT_TYPE_DELETE: DELETION,
            }
            content_type_id = ContentType.objects.get_for_model(self.model).pk
            for row in result:
                if row.import_type != row.IMPORT_TYPE_ERROR and row.import_type != row.IMPORT_TYPE_SKIP:
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=content_type_id,
                        object_id=row.object_id,
                        object_repr=row.object_repr,
                        action_flag=logentry_map[row.import_type],
                        change_message=_("%s through import_export" % row.import_type),
                    )
        """
