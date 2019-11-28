import json
from abc import ABCMeta, abstractproperty

from django import forms

from common.forms.DjangoQuerysetJSONEncoder


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
