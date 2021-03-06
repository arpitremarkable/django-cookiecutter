import base64
import json
from abc import ABC, abstractproperty

from django.shortcuts import get_object_or_404


class DataStoreFormViewMixin(ABC):
    """
    This ABC provides popular way of views dealing with forms that require DataStore model to store its form data
    """

    data_store_url_kwarg = 'data_store_id'

    @abstractproperty
    def data_store_model(self):
        pass

    def get_instance_kwargs(self):
        return {}

    def get_instance(self):
        """Gives data store instance for class usage"""
        if not hasattr(self, 'instance'):
            if self.data_store_url_kwarg in self.kwargs:
                kwargs = self.get_instance_kwargs()
                instance = get_object_or_404(self.data_store_model.objects, uuid=self.kwargs[self.data_store_url_kwarg], **kwargs)
            else:
                instance = self.data_store_model()
            setattr(self, 'instance', instance)
        return self.instance

    def get_form_kwargs(self, *args, **kwargs):
        """Add data store instance to form class kwargs"""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['instance'] = self.get_instance()
        return kwargs

    def get_initial(self):
        #     """
        #     Use data from data_store.data to prefill the form
        #     TODO: Check if data in data store is still valid for the current form
        #     """
        initial = super().get_initial()
        initial.update(self._get_initial_data_from_request())
        initial.update(self.get_instance().data)
        return initial

    def _get_initial_data_from_request(self):
        initial_data = base64.urlsafe_b64decode(self.request.GET.get('initial_data', ''))
        initial_data_cookie = self.request.COOKIES.get('initial_data')

        if initial_data:
            try:
                return json.loads(initial_data)
            except json.JSONDecodeError:
                return {}
        elif initial_data_cookie is not None:
            try:
                return json.loads(base64.urlsafe_b64decode(initial_data_cookie))
            except json.JSONDecodeError:
                return {}
        elif 'initial_data' in self.request.session:
            initial_data = self.request.session['initial_data']
            try:
                return json.loads(json.dumps(initial_data))
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
