# third party
from import_export.formats import base_formats

from . import xlsx


try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text



class XLSXBook(base_formats.XLSX):

    TABLIB_MODULE = '.xlsx'

    def get_format(self):
        """
        Import and returns tablib module.
        """
        return xlsx

    def fill_databook(self, databook, import_file):
        return self.get_format().import_book(databook, import_file)

    def export_databook(self, databook, **kwargs):
        return self.get_format().export_book(databook, **kwargs)
