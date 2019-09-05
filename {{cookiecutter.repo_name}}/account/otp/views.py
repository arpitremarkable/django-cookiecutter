import logging
from abc import ABC, abstractmethod

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

# third party
from account.communication import utils as communication_utils
from account.otp import utils
from {{cookiecutter.project_name}}.middleware.request import get_request

from . import exceptions
from . import forms as otp_forms
from . import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OTPView(FormView, ABC):
    form_class = otp_forms.OTPForm
    template_name = 'travel/form.pug'
    message_sent = False
    otp_service_response = dict()

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.request = get_request()
        return super(OTPView, self).__init__()

    @abstractmethod
    def get_phone_number(self):
        pass

    @abstractmethod
    def get_otp_key(self):
        pass

    def get_form_kwargs(self):
        kwargs = super(OTPView, self).get_form_kwargs()
        otp_service = utils.OTPGenerator(
            self.get_phone_number(),
            author=self.request.session._get_session_from_db())
        try:
            otp_instance = otp_service.get_latest_otp_instance()
        except exceptions.OTPGenerationException:
            otp_instance = None
        initial_data = dict()
        initial_data.update({"next": self.request.GET.get('next', '')})
        kwargs.update({
            "instance": otp_instance,
            "request": self.request,
            "initial": initial_data,
        })
        return kwargs

    def get(self, *args, **kwargs):
        phone_number = self.get_phone_number()
        otp_service = utils.OTPGenerator(phone_number, author=self.request.session._get_session_from_db())
        try:
            otp_instance = otp_service.get_or_create_otp()
        except exceptions.OTPGenerationException:
            messages.error(self.request, _("OTP Limit exceeded"))
        else:
            communication_service = communication_utils.Communicate(template_name="SMS__USER_VERIFICATION")
            service_response = communication_service.send_sms(phone_number, otp=otp_instance.generated_otp)
            self.message_sent = service_response.get('success')
            self.otp_service_response = service_response
        return super(OTPView, self).get(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        self.request.session[
            ':'.join([settings.OTP_CONFIG["otp_key_namespace"], self.get_otp_key()])
        ] = True
        response = redirect(form.cleaned_data.get("next", self.request.get_full_path()))
        return response
