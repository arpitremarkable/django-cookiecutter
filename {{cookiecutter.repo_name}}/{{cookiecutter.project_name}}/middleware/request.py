from threading import local


GLOBAL_REQUEST_KEEPER = local()

REQUEST_ATTR_NAME = '_local_request'


class GlobalRequestMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(GLOBAL_REQUEST_KEEPER, REQUEST_ATTR_NAME, request)
        try:
            return self.get_response(request)
        finally:
            delattr(GLOBAL_REQUEST_KEEPER, REQUEST_ATTR_NAME)


def get_request():
    return getattr(GLOBAL_REQUEST_KEEPER, REQUEST_ATTR_NAME, None)
