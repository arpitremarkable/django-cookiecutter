# third party
from django.contrib.contenttypes.models import ContentType

from account.otp import models as otp_models

from . import exceptions, settings


class OTPGenerator(object):

    def __init__(self, phone_number, author):
        if not phone_number:
            raise exceptions.InvalidPhoneNumberException
        self.phone_number = phone_number
        self.author = author
        return super(OTPGenerator, self).__init__()

    def __has_active_otp(self):
        return otp_models.OTPModel_pii.objects.for_author(self.author).for_phone(
            self.phone_number).in_current_timeframe().is_active(
                include_incorrect_attempt=True).exists()

    def __can_generate_otp(self):
        # Checks if otp generated in the timeframe > allowed OTPs
        return otp_models.OTPModel_pii.objects.for_author(self.author).for_phone(
            self.phone_number).in_current_timeframe().count() < settings.OTP_CONFIG["max_otp_retries"]

    def __record_otp_verification_request(self, otp):
        content_type = ContentType.objects.get(
            app_label=self.author._meta.app_label,
            model=self.author._meta.model_name)
        otp_models.OTPAttempt_pii.objects.create(
            author_type_id=content_type.id,
            author_id=self.author.pk,
            phone_number=self.phone_number,
            otp=otp)

    def get_or_create_otp(self):
        if self.__has_active_otp():
            return otp_models.OTPModel_pii.objects.for_author(self.author).for_phone(self.phone_number).is_active(
                include_incorrect_attempt=True).latest("created")
        elif self.__can_generate_otp():
            content_type = ContentType.objects.get(
                app_label=self.author._meta.app_label,
                model=self.author._meta.model_name)
            return otp_models.OTPModel_pii.objects.create(
                phone_number=self.phone_number,
                author_type_id=content_type.id,
                author_id=self.author.pk)
        else:
            raise exceptions.OTPGenerationException

    def get_latest_otp_instance(self):
        try:
            otp_instance = otp_models.OTPModel_pii.objects.for_author(self.author).for_phone(self.phone_number).is_active(
                include_incorrect_attempt=True).latest("created")
        except otp_models.OTPModel_pii.DoesNotExist:
            return None
        return otp_instance

    def validate_otp(self, otp):
        # Record OTP attempts
        self.__record_otp_verification_request(otp)
        if self.__has_active_otp():
            latest_otp = otp_models.OTPModel_pii.objects.for_author(self.author) \
                .for_phone(self.phone_number).in_current_timeframe() \
                .is_active(include_incorrect_attempt=True).latest("created")
            latest_otp.otp_verified = True if latest_otp.generated_otp == otp else False
            latest_otp.save(update_fields=['otp_verified'])
            return latest_otp.otp_verified
        return False
