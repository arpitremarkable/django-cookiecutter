from django.contrib.postgres import fields as pg_fields
from django.db import models

# third party
from common.models import TimeTrackedModel

from data_store.forms import DjangoQuerysetJSONEncoder


class PaymentGateway(TimeTrackedModel):
    request_data = pg_fields.JSONField(default=dict, encoder=DjangoQuerysetJSONEncoder)
    response_data = pg_fields.JSONField(default=dict, encoder=DjangoQuerysetJSONEncoder)
    is_success = models.BooleanField(default=False, editable=False)
