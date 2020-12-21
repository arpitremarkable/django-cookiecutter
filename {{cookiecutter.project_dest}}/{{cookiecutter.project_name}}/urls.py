"""{{cookiecutter.project_name}} URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
{%- if cookiecutter.feature_i18n == 'y' %}
from django.conf.urls.i18n import i18n_patterns
{%- endif %}
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

# third party
from watchman.views import bare_status


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='admin:index')),
    {%- if cookiecutter.feature_i18n == 'y' %}
    path('{{cookiecutter.project_name}}/i18n/', include('rosetta.urls')),
    {%- endif %}
    path('watchman/', include('watchman.urls')),
    path('watchman/bare-status/', bare_status),
]

urlpatterns += {{ 'i18n_patterns(' if cookiecutter.feature_i18n == 'y' else '[' }}
    path('{{cookiecutter.project_name}}/', admin.site.urls),
    path('domain/', include('domain.urls', namespace='domain')),
{{ ')' if cookiecutter.feature_i18n == 'y' else ']' }}

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "{{cookiecutter.project_name|title}} Administration"
admin.site.site_title = "{{cookiecutter.project_name|title}} Administration"

if settings.DEBUG:
    try:
        import debug_toolbar
    except ModuleNotFoundError:
        pass
    else:
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
