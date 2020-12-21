from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST


@require_POST
def accept_cookie_disclaimer(request):
    request.session['COOKIE_DISCLAIMER_ACCEPTED'] = True
    if request.is_ajax():
        return HttpResponse()
    else:
        return HttpResponseRedirect(request.path)
