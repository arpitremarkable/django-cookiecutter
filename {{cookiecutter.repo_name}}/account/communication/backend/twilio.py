# third party
import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


logger = logging.getLogger(__name__)
# account_sid = settings.get("TWILIO_ACCOUNT_SID")
# auth_token  = settings.get("TWILIO_AUTH_TOKEN")
account_sid = "AC32af5d9511b13e418b4949b9483068b3"
auth_token = "61a1cbfac3645c5e5d523de6b50139f4"

client = Client(account_sid, auth_token)


class TwilioCommunicator(object):

    def __init__(self, phone_number):
        self.phone_number = phone_number

    def send_sms(self, text):
        try:
            message = client.messages.create(
                to=self.phone_number,
                from_='+14343639410',
                body=text)
        except TwilioRestException as e:
            logger.error(
                'Communication backend API returned unexpected error',
                extra={
                    'exception': e.__class__.__name__,
                    'data': {
                        'exception_dict': e.__dict__
                    },
                    'tags': ['twilio', 'communication'],
                },
            )
            message = {
                "success": False,
                "description": getattr(e, "msg")
            }
        else:
            message = {"success": True, "data": getattr(message, "_properties")}
        return message
