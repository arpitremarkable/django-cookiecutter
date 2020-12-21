from django.urls import include, path

from . import views


app_name = "domain"

urlpatterns = [
    # path('travel/', include('domain.travel.urls', namespace='travel')),
    # path('car/', include('domain.car.urls', namespace='car')),
    path('accept-cookie-disclaimer/', views.accept_cookie_disclaimer, name='accept_cookie_disclaimer'),
]
