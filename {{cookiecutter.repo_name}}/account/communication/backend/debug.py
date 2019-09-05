import logging


logger = logging.getLogger(__name__)


class DebugCommunicator(object):

    def __init__(self, phone_number):
        self.phone_number = phone_number

    def send_sms(self, text):
        logger.info(text)
        return {"success": True}
