import requests
import datetime
import hashlib
import hmac
from .errors import FreekassaError, FreekassaAuthError
from collections import OrderedDict

ORDER_STATUSES = {
    0: 'Новый',
    1: 'Оплачен',
    8: 'Ошибка',
    9: 'Отмена'
}


def get_order_label(order_status):
    if order_status in ORDER_STATUSES:
        return ORDER_STATUSES.get(order_status)
    return 'Неизвестный статус'


class Freekassa:
    API_URL = 'https://api.freekassa.ru/v1/'
    API_BALANCE_ROUTE = 'balance'
    API_ORDERS_ROUTE = 'orders'
    API_ORDERS_CREATE_ROUTE = 'orders/create'
    API_WITHDRAWALS_ROUTE = 'withdrawals'
    API_WITHDRAWALS_CURRENCIES_ROUTE = 'withdrawals/currencies'
    API_WITHDRAWALS_CREATE_ROUTE = 'withdrawals/create'
    API_CURRENCIES_ROUTE = 'currencies'
    API_CURRENCIES_STATUS_ROUTE = 'currencies/%id%/status'
    API_SHOPS_ROUTE = 'shops'

    _api_key = ''
    _shop_id = 0
    _nonce = 0

    def __init__(self, api_key, shop_id):
        self._api_key = api_key
        self._shop_id = shop_id
        self._nonce = int(datetime.datetime.now().timestamp())

    def _get_url(self, route, **kwargs):
        url = f'{self.API_URL}{route}'
        for key, value in kwargs:
            url = url.replace(f'%{key}%', value)
        return url

    def _get_data(self, additional_fields=dict):
        data = OrderedDict({'shopId': self._shop_id, 'nonce': self._nonce})
        data.update(additional_fields)
        data.update({'signature': self._get_signature(data=data)})
        return data

    def _get_signature(self, data):
        return hmac.new(
            key=self._api_key.encode(),
            msg='|'.join(data).encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

    def _request(self, route, additional_fields=None, **kwargs):
        if additional_fields is None:
            additional_fields = {}
        response = requests.post(url=self._get_url(route, **kwargs), json=self._get_data(additional_fields))
        message = 'No message'
        if 'msg' in response.json():
            message = response.json().get('msg')
        if 'message' in response.json():
            message = response.json().get('message')
        if response.status_code == 400:
            raise FreekassaError(message)
        if response.status_code == 401:
            raise FreekassaAuthError(message)
        return response.json()

    @staticmethod
    def _get_time_str(dt: datetime.datetime):
        return dt.strftime('%Y.%m.%d %H:%M:%S')

    def get_balance(self):
        return self._request(self.API_BALANCE_ROUTE)

    def get_orders(self, order_id: int = None, payment_id: str = None, order_status: int = None,
                   date_from: datetime.datetime = None, date_to: datetime.datetime = None, page: int = None):
        additional_fields = {}
        if order_id:
            additional_fields['orderId'] = order_id
        if payment_id:
            additional_fields['paymentId'] = payment_id
        if order_status:
            additional_fields['orderStatus'] = order_status
        if date_from:
            additional_fields['dateFrom'] = self._get_time_str(date_from)
        if date_to:
            additional_fields['dateFrom'] = self._get_time_str(date_to)
        if page:
            additional_fields['page'] = page
        return self._request(self.API_ORDERS_ROUTE, additional_fields=additional_fields)

    def create_order(self, payment_system_id: int, email: str, ip: str, amount: float, currency_code: str = 'RUB',
                     payment_id: str = None, tel: str = None, success_url: str = None, failure_url: str = None,
                     notification_url: str = None):
        additional_fields = {'i': payment_system_id, 'email': email, 'ip': ip, 'amount': amount,
                             'currency': currency_code}
        if payment_id:
            additional_fields['paymentId'] = payment_id
        if tel:
            additional_fields['tel'] = tel
        if success_url:
            additional_fields['success_url '] = success_url
        if failure_url:
            additional_fields['failure_url'] = failure_url
        if notification_url:
            additional_fields['notification_url'] = notification_url
        return self._request(self.API_ORDERS_CREATE_ROUTE, additional_fields=additional_fields)

    def get_withdrawals(self, order_id: int = None, payment_id: str = None, order_status: int = None,
                        date_from: datetime.datetime = None, date_to: datetime.datetime = None, page: int = None):
        additional_fields = {}
        if order_id:
            additional_fields['orderId'] = order_id
        if payment_id:
            additional_fields['paymentId'] = payment_id
        if order_status:
            additional_fields['orderStatus'] = order_status
        if date_from:
            additional_fields['dateFrom'] = self._get_time_str(date_from)
        if date_to:
            additional_fields['dateFrom'] = self._get_time_str(date_to)
        if page:
            additional_fields['page'] = page
        return self._request(self.API_WITHDRAWALS_ROUTE, additional_fields=additional_fields)

    def create_withdrawal(self, payment_system_id: int, account: str, amount: float,
                          currency_code: str = 'RUB',
                          payment_id: str = None):
        additional_fields = {'i': payment_system_id, 'account': account, 'amount': amount, 'currency': currency_code}
        if payment_id:
            additional_fields['paymentId'] = payment_id
        return self._request(self.API_WITHDRAWALS_CREATE_ROUTE, additional_fields=additional_fields)

    def get_payment_systems(self):
        return self._request(self.API_CURRENCIES_ROUTE)

    def check_payment_system(self, payment_system_id):
        return self._request(self.API_CURRENCIES_STATUS_ROUTE, id=payment_system_id)

    def get_payment_systems_for_withdrawal(self):
        return self._request(self.API_WITHDRAWALS_CURRENCIES_ROUTE)

    def get_shops(self):
        return self._request(self.API_SHOPS_ROUTE)
