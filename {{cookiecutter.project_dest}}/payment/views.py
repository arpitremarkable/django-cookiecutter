import logging
from abc import ABC, abstractmethod

from django.conf import settings

# third party
import requests
from payment.models import PaymentGateway


logger = logging.getLogger('payment')


class PaymentGatewayException(Exception):
    pass


class PaymentGatewaysView(PaymentGatewayException, ABC):

    @abstractmethod
    def get_insurance_code(self):
        pass

    @abstractmethod
    def get_invoice_number(self, proposal):
        pass

    @abstractmethod
    def get_payment_product(self):
        pass

    @abstractmethod
    def get_payment_amount(self):
        pass

    @abstractmethod
    def get_payment_currency(self):
        pass

    @abstractmethod
    def get_payment_term(self):
        pass

    @abstractmethod
    def get_payment_smart_pay_id(self):
        pass

    @abstractmethod
    def get_user_session(self):
        pass

    @abstractmethod
    def get_success_url(self, proposal):
        pass

    @abstractmethod
    def get_another_information(self):
        pass

    def get_request_data(self, proposal):
        key = 'B553E9841389C-72544C7E8D9C9-3EFE3E1F7E5E8'
        insurance_code = self.get_insurance_code()
        invoice_number = self.get_invoice_number(proposal=proposal)
        payment_product = self.get_payment_product()
        payment_amount = self.get_payment_amount()
        payment_currency = self.get_payment_currency()
        payment_term = self.get_payment_term()
        payment_smart_pay_id = self.get_payment_smart_pay_id()
        success_url = self.get_success_url(proposal=proposal)
        user_session = self.get_user_session()
        another_information = self.get_another_information()

        request_data = {
            'key': key,
            'paymentDetails': {
                'insuranceCode': insurance_code,
                'invoiceNumber': invoice_number,
                'paymentProduct': payment_product,
                'paymentAmount': str(payment_amount),
                'paymentCurrency': payment_currency,
                'paymentTerm': payment_term,
                'paymentSmartPayID': payment_smart_pay_id,
            },
            'callbackURL': {
                'ifSession': user_session,
                'ifSuccess': success_url,
            },
            'anotherInformation': another_information,
        }
        return request_data

    def get_payment_url(self, request_data):
        try:
            if settings.DEBUG:
                token_payment_url = 'https://stg-payment.example.com/token'
            else:
                token_payment_url = 'https://payment.example.com/token'

            response = requests.post(token_payment_url, json=request_data)

        except requests.exceptions.RequestException as exception:
            raise Exception(exception)
        else:
            try:
                status_code = response.status_code

                if status_code != 200:
                    raise PaymentGatewayException
            except PaymentGatewayException as exception:
                logger.error(exception)
                logger.error(
                    'Request for payment gateway is failed with request %s', request_data)
            else:
                response_data = response.json()
                PaymentGateway.objects.create(
                    request_data=request_data,
                    response_data=response_data,
                    is_success=True,
                )
                payment_url = response_data['body']['paymentLink']

                return payment_url
