# third party
from import_export import widgets
from psycopg2.extras import NumericRange


class IntegerRangeWidget(widgets.SimpleArrayWidget):

    def clean(self, value, row=None, *args, **kwargs):
        value = super().clean(value=value, row=row, *args, **kwargs)
        if len(value):
            return NumericRange(int(value[0]), int(value[1]))
        else:
            return None

    def render(self, value, obj=None):
        return self.separator.join([str(value.lower), str(value.upper)])
