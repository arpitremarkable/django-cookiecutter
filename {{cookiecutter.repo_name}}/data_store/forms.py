import json
from abc import ABCMeta, abstractproperty

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import (
    FlatValuesListIterable, QuerySet, ValuesIterable, ValuesListIterable,
)
from django.utils.functional import LazyObject, empty


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


class DataStoreMeta(ABCMeta, forms.forms.DeclarativeFieldsMetaclass):
    pass


class DataStoreMixin(metaclass=DataStoreMeta):
    """
    Mixin to provide any django form with a functionality to store it's validated data
    into a DataStore subclassed model.
    """

    def __init__(self, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    @abstractproperty
    def form_name(self):
        """A unique identifier for the datastore. eg: 'homepage registration form'"""
        pass

    @abstractproperty
    def current_version(self):
        """
        Incrementing integer starting from 1.
        Increment everytime there are changes in the form
        """
        pass

    def cleaned_data_to_json(self):
        return json.dumps(self.cleaned_data, cls=DjangoQuerysetJSONEncoder)

    def save(self, commit=True):
        """
        Saves form's data (form.data) to a datastore instance.
        Be sure to use form.is_valid() before saving to the database
        """
        self.instance.data = self.data
        self.instance.cleaned_data = json.loads(self.cleaned_data_to_json())
        self.instance.name = self.form_name
        self.instance.fields = list(self.fields.keys())
        if commit:
            self.instance.save()
        return self.instance
