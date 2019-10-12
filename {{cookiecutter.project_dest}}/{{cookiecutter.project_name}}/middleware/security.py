import logging
import re

from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)


class ELBMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if 'HTTP_X_FORWARDED_PROTO' in request.META:
            if request.META['HTTP_X_FORWARDED_PROTO'] == 'http':
                return HttpResponsePermanentRedirect(
                    "https://%s%s" % (request.get_host(), request.get_full_path())
                )


class HeadersLoggingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        keys = sorted(filter(lambda k: re.match(r'(HTTP_|CONTENT_)', k), request.META))
        keys = ['REMOTE_ADDR'] + keys
        meta = ''.join("%s=%s\n" % (k, request.META[k]) for k in keys)
        logger.info('%s %s\n%s\n' % (request.method, request.build_absolute_uri(), meta))
