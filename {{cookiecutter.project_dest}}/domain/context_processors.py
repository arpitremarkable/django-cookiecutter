from django.apps import apps
from django.conf import settings
from django.urls import resolve, reverse
from django.utils import formats
{%- if cookiecutter.feature_i18n == 'y' %}
from django.utils.translation import activate, get_language
{% endif %}


def django_settings(request):
    return {
        'settings': settings,
    }


{%- if cookiecutter.feature_i18n == 'y' %}
def change_language(request):
    def change_language_func(lang, path=None):
        """
        Get current page in specified language
        """
        path = path or request.path
        url_parts = resolve(path)
        cur_language = get_language()
        try:
            activate(lang)
        except Exception:
            url = path
        else:
            url = reverse(url_parts.view_name, kwargs=url_parts.kwargs)
        finally:
            activate(cur_language)
        return "%s" % url

    return {
        'change_language': change_language_func,
    }

def interpolate_language_code(request):
    def interpolate(string):
        """
        for example: changes '__%(lang)s' to __th
        """
        return string % {'lang': get_language()}
    return {
        'l': interpolate,
    }
{% endif %}


def misc(request):
    app_names = request.resolver_match.app_names
    if 'domain.travel' in app_names:
        category = 'travel'
    elif 'domain.car' in app_names:
        category = 'car'
    else:
        category = settings.DEFAULT_CATEGORY
    return {
        'COOKIE_DISCLAIMER_ACCEPTED': request.session.get('COOKIE_DISCLAIMER_ACCEPTED', False),
        'LOCAL_DATE_FORMAT': formats.get_format('DATE_FORMAT'),
        'CATEGORY': category,
        'BASE_TEMPLATE': f'{category}/mobile.pug' if request.user_agent.is_mobile else f'{category}/desktop.pug',
        'SESSION_ID': (
            request.session.session_key
            if apps.is_installed('django.contrib.sessions')
            else None  # Use this ID to be sent to analytics apps.
        )
    }
