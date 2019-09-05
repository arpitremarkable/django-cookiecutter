from django.shortcuts import redirect

from . import settings, views


class _OTPRequired(object):

    def __init__(self, function, override_view, redirect_url, unless):
        self.function = function
        self.otp_view = override_view or views.OTPView
        self.redirect_url = redirect_url
        self.unless = unless

    def __call__(self, *args, **kwargs):
        request = args[0]
        if self.unless and self.unless(request):
            return self.function(*args, **kwargs)
        else:
            otp_response_view = self.otp_view(request, **kwargs)
            otp_key = ':'.join([settings.OTP_CONFIG["otp_key_namespace"], otp_response_view.get_otp_key()])
            if request.session.get(otp_key):
                return self.function(*args, **kwargs)
            elif self.redirect_url:
                response = redirect(self.redirect_url, **kwargs)
                response['Location'] += '?next={}'.format(request.get_full_path())
                return response
            else:
                return otp_response_view.dispatch(request, *args, **kwargs)


def otp_required(function=None, override_view=None, redirect_url=None, unless=None):
    if function:
        return _OTPRequired(function=function, override_view=override_view, redirect_url=redirect_url, unless=unless)
    else:
        def wrapper(function):
            return _OTPRequired(function=function, override_view=override_view, redirect_url=redirect_url, unless=unless)
        return wrapper
