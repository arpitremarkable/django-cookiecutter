import collections


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


{%- if cookiecutter.feature_multilang == 'y' %}
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
