# third party
from django.conf import settings
from django.template import Context, Template

from account.communication.backend.debug import DebugCommunicator
from account.communication.backend.twilio import TwilioCommunicator


COMMUNICATION_BACKENDS = {
    "default": TwilioCommunicator,
    "debug": DebugCommunicator,
    "twilio": TwilioCommunicator,
}

TEMPLATES = {
    "SMS__USER_VERIFICATION": "รหัส OTP สำหรับยืนยันการซื้อประกันภัยออนไลน์กับเอกอนไดเร็คท์ของคุณคือ {{otp}}",
}


class Communicate(object):

    def __init__(self, template_name, backend="twilio"):
        if template_name and template_name not in TEMPLATES:
            raise KeyError
        self.template = TEMPLATES[template_name]
        if settings.DEBUG:
            backend = 'debug'
        self.communication_channel = COMMUNICATION_BACKENDS.get(backend, 'default')

    def send_sms(self, phone_number, **kwargs):
        communication_service = self.communication_channel(phone_number)
        text = Template(self.template).render(Context(kwargs))
        return communication_service.send_sms(text)
