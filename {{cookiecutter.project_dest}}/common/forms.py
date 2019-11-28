import collections

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import (
    FlatValuesListIterable, QuerySet, ValuesIterable, ValuesListIterable,
)
from django.utils.functional import LazyObject, empty


class GetFieldMixin(object):
    """
    This mixin is used so that
    `form.get_field(name=field_name)`
    is possible to do inside template files
    when field object is needed
    """
    def get_field(self, name):
        if isinstance(name, collections.Iterable) and not isinstance(name, str) and all(hasattr(self, field_name) for field_name in name):
            return_val = [self[field_name] for field_name in name]
        else:
            return_val = self[name]
        return return_val


{%- if cookiecutter.feature_i18n == 'y' %}
class LanguageSwitchableFormMixin(object):
    '''
        Input params:
            current_language variable to be provided in the kwargs(request.LANGUAGE_CODE)
        Behaviour:
            exposes a get_current_language method to take actions as per the language provided
            In certain forms, the insurer expects different values for dropdown for different languages
            This behaviour can be accomplished by switching the form as per get_current_language
            functionality added by this mixin
    '''
    _current_language = None

    def __init__(self, *args, **kwargs):
        if "current_language" in kwargs:
            self._current_language = kwargs.pop('current_language')
        super().__init__(*args, **kwargs)

    def get_current_language(self):
        return self._current_language
{% endif %}


class DjangoQuerysetJSONEncoder(DjangoJSONEncoder):
    def default(self, value):
        if isinstance(value, LazyObject):
            if value._wrapped is empty:
                value._setup()
            return value._wrapped

        if isinstance(value, QuerySet):
            # Couldn't find a way without using private variables
            if value._iterable_class in (ValuesIterable,
                                         ValuesListIterable,
                                         FlatValuesListIterable):
                return [v for v in value]
            else:
                return [self.default(v) for v in value]
        elif isinstance(value, models.Model):
            d = {
                'pk': value.pk,
                'app_label': value._meta.app_label,
                'model_name': value._meta.model_name,
                'str': str(value),
            }
            if hasattr(value, 'natural_key'):
                d.update({'natural': value.natural_key()})
            return d
        return super(DjangoQuerysetJSONEncoder, self).default(value)
