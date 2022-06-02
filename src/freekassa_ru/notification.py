import hashlib
from .errors import FreekassaNotificationError

FREEKASSA_NOTIFICATION_IP_LIST = ['168.119.157.136', '168.119.60.227', '138.201.88.124', '178.154.197.79']


class Notification:
    shop_id = None
    amount = None
    freekassa_id = None
    order_id = None
    email = None
    phone = None
    currency_id = None
    sing = None
    additional_parameters = None
    payer_account = None
    tax = None
    secret2 = None
    ip = None

    def __init__(self, data, secret2, ip=None):
        self.shop_id = data.get('MERCHANT_ID')
        self.amount = data.get('AMOUNT')
        self.freekassa_id = data.get('intid')
        self.payment_id = data.get('MERCHANT_ORDER_ID')
        self.email = data.get('P_EMAIL')
        self.phone = data.get('P_PHONE')
        self.currency_id = data.get('CUR_ID')
        self.sing = data.get('SIGN')
        self.payer_account = data.get('payer_account')
        self.tax = data.get('commission')
        self.additional_parameters = {key: val for key, val in data.items() if 'us_' in key}
        self.secret2 = secret2
        self.ip = ip

    def check_signature(self):
        if not hashlib.md5(
                f'{self.shop_id}:{self.amount}:{self.secret2}:{self.payment_id}'.encode()).hexdigest() == self.sing:
            raise FreekassaNotificationError(f'Invalid signature')

    def check_ip(self):
        if self.ip not in FREEKASSA_NOTIFICATION_IP_LIST:
            raise FreekassaNotificationError(f'Ip must be in {", ".join(FREEKASSA_NOTIFICATION_IP_LIST)}')

    def check(self):
        self.ip and self.check_ip()
        self.check_signature()
        return 'YES'
