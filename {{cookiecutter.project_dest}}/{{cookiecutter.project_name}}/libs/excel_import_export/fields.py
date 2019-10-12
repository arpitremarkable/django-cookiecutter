from django import VERSION
from django.contrib.contenttypes.models import ContentType

# third party
from import_export import fields as base_fields
from parse import parse

from . import utils


class ExcelField(base_fields.Field):

    def export(self, obj, row_no, res_map):
        """
        Returns value from the provided object converted to export
        representation.
        """
        value = self.get_value(obj)
        if value is None:
            return ""
        return self.widget.render(value, obj)

    def clean(self, data, res_map):
        try:
            return data[self.column_name]
        except KeyError:
            raise KeyError("Column '%s' not found in dataset. Available "
                           "columns are: %s" % (self.column_name, list(data)))

    def save(self, obj, data, is_m2m, res_map):
        """
        If this field is not declared readonly, the object's attribute will
        be set to the value returned by :meth:`~import_export.fields.Field.clean`.
        """
        if not self.readonly:
            attrs = self.attribute.split('__')
            for attr in attrs[:-1]:
                obj = getattr(obj, attr, None)
            cleaned = self.clean(data, res_map)
            if cleaned is not None or self.saves_null_values:
                if VERSION < (1, 9, 0):
                    setattr(obj, attrs[-1], cleaned)
                if not is_m2m:
                    setattr(obj, attrs[-1], cleaned)
                else:
                    getattr(obj, attrs[-1]).set(cleaned)


class UniqueKeyField(ExcelField):

    def __init__(self, model, fields):
        self.model = model
        self.fields = fields
        self._sheet_title = utils.get_sheet_title(self.model)
        super(UniqueKeyField, self).__init__(
            attribute='unique_key', column_name='unique_key'
        )

    def col_map(self, res_map):
        return res_map[self._sheet_title]['col_map']

    def export(self, obj, row_no, res_map):
        # '=A1&"-"&B1&"-"&C1&"-"&D1'
        cell_list = ["{col}{row}".format(col=self.col_map(res_map)[field], row=row_no) for field in self.fields]
        return '=' + '&"-"&'.join(cell_list)

    def save(self, obj, data, is_m2m, res_map):
        return None


class ForeignKeyField(ExcelField):

    def __init__(self, model, field):
        self.model = model
        self.field = field
        self._sheet_title = utils.get_sheet_title(self.model)
        super(ForeignKeyField, self).__init__(
            attribute=self.field, column_name=self.field
        )

    def get_queryset(self):
        return self.model.objects.all()

    def clean(self, data, res_map):
        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError("Column '%s' not found in dataset. Available "
                           "columns are: %s" % (self.column_name, list(data)))
        if value:
            value = value.replace('$', '')
            parse_result = parse('={sheet_title}!A{row_no}', value)
            if not parse_result:
                raise Exception

            parse_result = parse_result.named
            if not parse_result['sheet_title'] == self._sheet_title:
                raise Exception

            row_no = parse_result['row_no']
            value = res_map[self._sheet_title]['row_map'][row_no]
        return value

    def get_value(self, obj):
        return getattr(obj, self.field)

    def get_obj_row_no(self, res_map, obj):
        return res_map[self._sheet_title]['row_map'][str(obj)]

    def export(self, obj, row_no, res_map):
        # '=foreign_table_sheet_title!A21'
        value = self.get_value(obj)
        if value is None:
            return ""
        return '={sheet_title}!A{row_no}'.format(
            sheet_title=self._sheet_title,
            row_no=self.get_obj_row_no(res_map, value)
        )


class ContentTypeField(ExcelField):

    def __init__(self, app_label):
        self.app_label = app_label
        super(ContentTypeField, self).__init__(
            attribute='_content_type', column_name='content type'
        )

    def get_queryset(self):
        return ContentType.objects.filter(app_label=self.app_label)

    def clean(self, data, res_map):
        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError("Column '%s' not found in dataset. Available "
                           "columns are: %s" % (self.column_name, list(data)))
        return self.get_queryset().get(model=value) if value else None

    def export(self, obj, row_no, res_map):
        value = self.get_value(obj)
        if value is None:
            return ""
        return value.model


class ManyToManyField(ForeignKeyField):

    def get_value(self, obj):
        return getattr(obj, self.field).first()

    def clean(self, data, res_map):
        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError("Column '%s' not found in dataset. Available "
                           "columns are: %s" % (self.column_name, list(data)))
        values = []
        if value:
            value = value.replace('$', '')
            places = value.split('&')
            if len(places) > 1:
                values = []
                for index, place in enumerate(places):
                    if index != 0:
                        place = '=' + place
                    parse_result = parse('={sheet_title}!A{row_no}', place)
                    if not parse_result:
                        raise Exception

                    parse_result = parse_result.named
                    if not parse_result['sheet_title'] == self._sheet_title:
                        raise Exception

                    row_no = parse_result['row_no']
                    value = res_map[self._sheet_title]['row_map'][row_no]
                    values.append(value)
            else:
                parse_result = parse('={sheet_title}!A{row_no}', value)
                if not parse_result:
                    raise Exception

                parse_result = parse_result.named
                if not parse_result['sheet_title'] == self._sheet_title:
                    raise Exception

                row_no = parse_result['row_no']
                value = res_map[self._sheet_title]['row_map'][row_no]
                values = [value]

        return values if values else []


class TreeForeignKeyField(ForeignKeyField):

    def clean(self, data, res_map):
        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError("Column '%s' not found in dataset. Available "
                           "columns are: %s" % (self.column_name, list(data)))

        if value:
            value = value.replace('$', '')
            parse_result = parse('=A{row_no}', value)
            if not parse_result:
                raise Exception

            parse_result = parse_result.named

            row_no = parse_result['row_no']
            value = res_map[self._sheet_title]['row_map'][row_no]

        return value

    def export(self, obj, row_no, res_map):
        value = self.get_value(obj)
        if value is None:
            return ""
        return '=A{row_no}'.format(
            row_no=self.get_obj_row_no(res_map, value)
        )
