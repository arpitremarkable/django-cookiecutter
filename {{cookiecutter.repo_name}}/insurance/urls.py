from django.urls import include, path

from . import views


app_name = "insurance"

urlpatterns = [
    # path('travel/', include('insurance.travel.urls', namespace='travel')),
    # path('car/', include('insurance.car.urls', namespace='car')),
    path('accept-cookie-disclaimer/', views.accept_cookie_disclaimer, name='accept_cookie_disclaimer'),
]
