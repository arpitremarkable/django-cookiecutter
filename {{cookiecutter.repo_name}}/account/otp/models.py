# Create your models here.
import random

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone

# third party
from common.models import TimeTrackedModel

from . import settings


def generate_otp():
    otp_length = settings.OTP_CONFIG["length"]
    range_start = 10**(otp_length-1)
    range_end = (10**otp_length)-1
    return str(random.randint(range_start, range_end))


class OTPQueryset(models.QuerySet):

    def for_author(self, author):
        author_type = ContentType.objects.get_for_model(author)
        author_id = author.pk
        return self.filter(author_type=author_type, author_id=author_id)

    def for_phone(self, phone_number):
        return self.filter(phone_number=phone_number)

    def in_current_timeframe(self):
        current_time = timezone.now()
        return self.filter(
            created__range=(
                current_time - timezone.timedelta(seconds=settings.OTP_CONFIG["otp_valid_window"]),
                current_time,
            ),
        )

    def is_active(self, include_incorrect_attempt=None):
        otp_verified_filter = Q(otp_verified__isnull=True)
        if include_incorrect_attempt:
            otp_verified_filter |= Q(otp_verified=False)
        return self.filter(
            otp_verified_filter,
        )


class OTPModelManager(models.Manager):

    def get_queryset(self):
        return OTPQueryset(self.model, using=self._db)

    def for_author(self, author):
        return self.get_queryset().for_author(author)

    def for_phone(self, phone_number):
        return self.get_queryset().for_phone(phone_number)

    def in_current_timeframe(self):
        return self.get_queryset().in_current_timeframe()

    def is_active(self, include_incorrect_attempt=False):
        return self.get_queryset().is_active(include_incorrect_attempt)


class OTPModel(TimeTrackedModel):
    '''
        DEPRECATED MODEL: Please don't use this.
        TODO: Cleanup Q2
    '''
    #  session
    phone_number = models.CharField(max_length=20)  # max length
    generated_otp = models.CharField(max_length=settings.OTP_CONFIG["length"], default=generate_otp)
    otp_verified = models.NullBooleanField(default=None)
    author_type = models.ForeignKey(
        ContentType, db_constraint=False, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_authored",
    )
    author_id = models.CharField(max_length=128)
    author = GenericForeignKey('author_type', 'author_id')
    objects = OTPModelManager()

    def __str__(self):
        return f"{self.pk}: {self.phone_number} <-> {self.author.pk}"

    class Meta:
        db_table = "otp_otpmodel__deprecated"


class OTPAttempt(TimeTrackedModel):
    '''
        DEPRECATED MODEL: Please don't use this.
        TODO: Cleanup Q2
    '''
    phone_number = models.CharField(max_length=20)  # max length
    author_type = models.ForeignKey(
        ContentType, db_constraint=False, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_authored",
    )
    author_id = models.CharField(max_length=128)
    author = GenericForeignKey('author_type', 'author_id')
    otp = models.CharField(max_length=settings.OTP_CONFIG["length"])

    def __str__(self):
        return f"{self.pk}: {self.phone_number} <-> {self.author.pk}"

    class Meta:
        db_table = "otp_otpattempt__deprecated"


class OTPModel_pii(TimeTrackedModel):
    _DATABASE = "pii"
    phone_number = models.CharField(max_length=20)  # max length
    generated_otp = models.CharField(max_length=settings.OTP_CONFIG["length"], default=generate_otp)
    otp_verified = models.NullBooleanField(default=None)
    author_type = models.ForeignKey(
        ContentType, db_constraint=False, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_authored",
    )
    author_id = models.CharField(max_length=128)
    author = GenericForeignKey('author_type', 'author_id')
    objects = OTPModelManager()

    def __str__(self):
        return f"{self.pk}: {self.phone_number} <-> {self.author.pk}"

    class Meta:
        db_table = "otp_otpmodel"


class OTPAttempt_pii(TimeTrackedModel):
    _DATABASE = "pii"
    phone_number = models.CharField(max_length=20)  # max length
    author_type = models.ForeignKey(
        ContentType, db_constraint=False, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_authored",
    )
    author_id = models.CharField(max_length=128)
    author = GenericForeignKey('author_type', 'author_id')
    otp = models.CharField(max_length=settings.OTP_CONFIG["length"])

    def __str__(self):
        return f"{self.pk}: {self.phone_number} <-> {self.author.pk}"

    class Meta:
        db_table = "otp_otpattempt"
