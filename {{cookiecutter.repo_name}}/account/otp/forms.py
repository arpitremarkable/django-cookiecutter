from django import forms

# third party
from account.otp import models as otp_models
from account.otp import utils as otp_utils
from common.forms import GetFieldMixin

from . import settings


class OTPForm(GetFieldMixin, forms.ModelForm):
    otp = forms.CharField(max_length=settings.OTP_CONFIG["length"])
    next = forms.CharField(max_length=100, required=False)

    class Meta:
        model = otp_models.OTPModel_pii
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(OTPForm, self).__init__(*args, **kwargs)
        self.fields['next'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'otp' in cleaned_data:
            otp = cleaned_data["otp"]
            phone_number = self.instance.phone_number
            try:
                is_otp_valid = otp_utils.OTPGenerator(
                    phone_number, self.request.session._get_session_from_db()).validate_otp(otp)
            except otp_models.OTPModel_pii.DoesNotExist:
                self.add_error('otp', 'Invalid OTP/OTP Expired')
            else:
                if not is_otp_valid:
                    self.add_error('otp', "Wrong OTP")
