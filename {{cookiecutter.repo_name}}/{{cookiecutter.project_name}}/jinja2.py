from django.utils.translation import gettext, ngettext

# third party
from bootstrap4.templatetags import bootstrap4
from jinja2 import Environment
from static_precompiler.templatetags.compile_static import compile_filter


def environment(**options):
    env = Environment(**options)
    env.install_gettext_callables(gettext=gettext, ngettext=ngettext, newstyle=True)
    env.globals.update({
        'bs4': bootstrap4,
        'compile': compile_filter,
    })
    return env
