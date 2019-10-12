import logging

from django.conf import settings
from django.contrib.postgres import fields as pg_fields
from django.db import models
from django.utils import timezone

# third party
from django_countries.fields import CountryField
# GEOIP_CACHE_TYPE = getattr(settings, 'GEOIP_CACHE_TYPE', 4)
from model_utils import Choices

from data_store.forms import DjangoQuerysetJSONEncoder


# from analytics.settings import TRACK_USING_GEOIP

# from django.contrib.gis.geoip import HAS_GEOIP
# if HAS_GEOIP:
#     from django.contrib.gis.geoip import GeoIP, GeoIPException


log = logging.getLogger(__file__)


class TimeTrackedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Visitor(TimeTrackedModel):
    session_key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    landing_url = models.URLField(max_length=2048, default=None)
    expiry_age = models.IntegerField(null=True, editable=False)
    expiry_time = models.DateTimeField(null=True, editable=False)
    time_on_site = models.IntegerField(null=True, editable=False)
    user_agent = models.TextField(null=True, editable=False)
    data = pg_fields.JSONField(default=dict, encoder=DjangoQuerysetJSONEncoder)

    def __str__(self):
        return f'{self.session_key} - {self.user}'

    def session_expired(self):
        """The session has ended due to session expiration."""
        if self.expiry_time:
            return self.expiry_time <= timezone.now()
        return False
    session_expired.boolean = True

    def session_ended(self):
        """The session has ended due to an explicit logout."""
        return bool(self.end_time)
    session_ended.boolean = True

    class Meta(object):
        ordering = ('-created',)


class WebEvent(TimeTrackedModel):
    modified = None
    METHOD_TYPES = Choices(
        'GET',
        'POST',
    )
    DEVICE_TYPES = Choices(
        'PC',
        'MOBILE',
        'TABLET',
        'BOT',
        'UNKNOWN',
    )
    visitor = models.ForeignKey('Visitor', on_delete=models.PROTECT)
    data = pg_fields.JSONField(default=dict, encoder=DjangoQuerysetJSONEncoder)
    marketing_params = pg_fields.HStoreField(default=dict)
    referrer = models.URLField(max_length=2048)
    url = models.URLField(max_length=2048)
    url_kwargs = pg_fields.HStoreField(default=dict)
    url_name = models.CharField(max_length=100)
    response_data = pg_fields.HStoreField(default=dict)
    status_code = models.IntegerField()
    method = models.CharField(max_length=6, choices=METHOD_TYPES)

    # from user agent
    browser = models.CharField(max_length=30)
    browser_version = models.CharField(max_length=30)
    os = models.CharField(max_length=100)
    os_version = models.CharField(max_length=30)
    device_model = models.CharField(max_length=30)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)

    ip_address = models.GenericIPAddressField(max_length=39, null=True)
    ip_country = CountryField()
    ip_region = models.CharField(max_length=255)
    ip_city = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.visitor_id} - {self.method} - {self.url_name}'

    class Meta:
        ordering = ['created']
