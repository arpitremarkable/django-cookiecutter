from django.urls import include, path


app_name = "account"

urlpatterns = [
    path('otp/', include(('account.otp.urls', 'otp'), namespace='otp')),
]
