import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields
from django.db import models

# third party
from model_utils import FieldTracker
from model_utils.models import TimeStampedModel
from {{cookiecutter.project_name}}.middleware.request import get_request


class DataStoreManager(models.Manager):

    def get_request(self):
        return get_request()

    def get_queryset(self):
        request = self.get_request()
        qs = super(DataStoreManager, self).get_queryset()
        if request and not (request.user.is_superuser or request.user.is_staff):
            session_object = request.session._get_session_from_db()
            if session_object:
                ContentType.objects.get_for_model(session_object._meta.model)
                return qs.filter(
                    author_type=ContentType.objects.get_for_model(session_object._meta.model),
                    author_id=session_object.pk,
                )
            else:
                return qs.none()
        else:
            return qs


# Use this model only as a parent for other concreate models that require flexi data store functionalities
class DataStore(TimeStampedModel):
    name = pg_fields.CICharField(max_length=200)
    version = models.IntegerField(default=1)
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4, editable=False)
    data = pg_fields.JSONField(default=dict)
    cleaned_data = pg_fields.JSONField(default=dict)
    fields = pg_fields.ArrayField(models.CharField(max_length=200), default=list)
    field_tracker = FieldTracker(fields=['data', 'cleaned_data', 'fields'])
    author_type = models.ForeignKey(
        ContentType, db_constraint=False, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_authored",
    )
    author_id = models.CharField(max_length=128)
    author = GenericForeignKey('author_type', 'author_id')

    objects = DataStoreManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        request = get_request()
        if not self.pk:
            if request:
                if not request.session.session_key:
                    request.session.save()
                session_object = request.session._get_session_from_db()
                self.author_type_id = ContentType.objects.get_for_model(session_object._meta.model).id
                self.author_id = session_object.pk
        return super().save(*args, **kwargs)
