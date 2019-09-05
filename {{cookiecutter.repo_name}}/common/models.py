from django.contrib.contenttypes.fields import ContentType, GenericForeignKey
from django.db import models


class AbstractModelMixin(object):

    def __str__(self):
        try:
            return self.name
        except Exception:
            try:
                return self.title
            except Exception:
                return ''


class AbstractModel(AbstractModelMixin, models.Model):

    class Meta:
        abstract = True


class TimeTrackedModel(AbstractModel):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractGenericModel(AbstractModel):
    _content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    special_object = GenericForeignKey('_content_type', 'id')

    def save(self, *args, **kwargs):
        self.special_object = self
        return super(AbstractGenericModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
