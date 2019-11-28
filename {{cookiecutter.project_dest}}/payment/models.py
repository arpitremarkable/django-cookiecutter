from django.contrib.postgres import fields as pg_fields
from django.db import models

# third party
from common.forms import DjangoQuerysetJSONEncoder
from common.models import TimeTrackedModel


class PaymentGateway(TimeTrackedModel):
    request_data = pg_fields.JSONField(default=dict, encoder=DjangoQuerysetJSONEncoder)
    response_data = pg_fields.JSONField(default=dict, encoder=DjangoQuerysetJSONEncoder)
    is_success = models.BooleanField(default=False, editable=False)
