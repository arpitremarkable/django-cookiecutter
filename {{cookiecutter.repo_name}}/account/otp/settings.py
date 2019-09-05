from django.conf import settings


OTP_CONFIG = {
    "length": 6,
    "otp_valid_window": 15*60,  # seconds
    "max_otp_retries": 3,
    "otp_key_namespace": 'OTPKEY',
}

if hasattr(settings, "OTP_CONFIG"):
    OTP_CONFIG.update(settings.OTP_CONFIG)
