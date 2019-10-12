"""{{cookiecutter.project_name}} URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# third party
from watchman.views import bare_status


urlpatterns = [
    path('{{cookiecutter.project_name}}/i18n/', include('rosetta.urls')),
    path('watchman/', include('watchman.urls')),
    path('watchman/bare-status/', bare_status),
]

urlpatterns += i18n_patterns(
    path('{{cookiecutter.project_name}}/', admin.site.urls),
)

urlpatterns += i18n_patterns(
    path('insurance/', include('insurance.urls', namespace='insurance')),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Aegon Direct Administration"
admin.site.site_title = "Aegon Direct Administration"

if settings.DEBUG:
    try:
        import debug_toolbar
    except ModuleNotFoundError:
        pass
    else:
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns