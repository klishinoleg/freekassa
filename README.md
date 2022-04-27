# freekassa

# Установка

pip install freekassa-ru

# Использование API

```
from freekassa_ru import Freekassa


SHOP_ID = ''
API_KEY = ''
fk = Freekassa(shop_id=SHOP_ID, api_key=API_KEY)
```

## Запрос баланса

```
fk.get_balance() 
```

```
    {
        "type": "success",
        "balance": 
        [
            {
                "currency": "RUB",
                "value": 743.43
            }
        ]
    }
```

## Список заявок

```
list = fk.get_orders()
```

Фильтрация:

- order_id: int = None,
- payment_id: str = None,
- order_status: int = None,
- date_from: datetime.datetime = None,
- date_to: datetime.datetime = None,
- page: int = None

```
    {
        "type": "success",
        "pages": 12,
        "orders": 
            [
                {
                "merchant_order_id": "Order #123",
                "fk_order_id": 652367,
                "amount": 100.12,
                "currency": "RUB",
                "email": "user@site.ru",
                "account": "5555555555554444",
                "date": "2021-03-29 12:28:24",
                "status": 1
                }
            ]
    }
```

### Получить название статуса:

```
from freekassa_ru import get_order_label

print(get_order_label(order.get('status')))
```

## Создать заказ и получить ссылку на оплату

```
payment_system_id = 1
email = 'test@test.ru'
ip = '0.0.0.0'
amount = 110.20
list = fk.create_order(payment_system_id, email, ip, amount)
```

Параметры:

- payment_system_id: int, ID платежной системы
- email: str, Электронный адрес плательщика
- ip: str, IP плательщика
- amount: float, сумма платежа
- currency_code: str = 'RUB', символьный код валюты оплаты
- payment_id: str = None, Номер заказа в Вашем магазине
- tel: str = None, телефон плательщика
- success_url: str = None, Переопределение урла успеха (для включения данного параметра обратитесь в поддержку)
- failure_url: str = None, Переопределение урла ошибки (для включения данного параметра обратитесь в поддержку)
- notification_url: str = None, Переопределение урла уведомлений (для включения данного параметра обратитесь в
  поддержку)

```
    {
        "type": "success",
        "orderId": 123,
        "orderHash": "bd4161db429848651499aabcb1d89330",
        "location": "https://pay.freekassa.ru/form/123/bd4161db429848651499aabcb1d89330"
    }
```

## Список выплат

```
fk.get_withdrawals()
```

Фильтры аналогичные списку заявок

## Создать выплату

```
payment_system_id = 1
amount = 110.20
account = '5500000000000004'
fk.create_withdrawal(self, payment_system_id: int, account: str, amount: float)
```

Параметры:

- payment_system_id: int, ID платежной системы
- account: str, Кошелек для зачисления средств (при выплате на FKWallet вывод осуществляется только на свой аккаунт)
- amount: float, сумма платежа
- currency_code: str = 'RUB', символьный код валюты оплаты
- payment_id: str = None, Номер заказа в Вашем магазине

```
    {
      "type": "success",
      "data": {
        "id": 185
        }
    }
```

## Получение списка доступных платежных систем

```
fk.get_payment_systems() 
```

```
  {
    "type": "success",
    "currencies": [
        {
        "id": 4,
        "name": "VISA",
        "currency": "RUB",
        "is_enabled": 1,
        "is_favorite": 0
        }
    ]
}
```

## Проверка доступности платежной системы для оплаты

```
payment_system_id = 1
fk.check_payment_system(payment_system_id)
```

```
  {
      "type": "success"
  }
```

## Получение списка доступных платежных систем для вывода

```
fk.get_payment_systems_for_withdrawal() 
```

```
{
  "type": "success",
  "currencies": [
    {
      "id": 4,
      "name": "VISA",
      "min": 100,
      "max": 15000,
      "currency": "RUB",
      "can_exchange": 1
    }
  ]
}
```

## Получение списка Ваших магазинов

```
fk.get_shops() 
```

```
{
  "type": "success",
  "shops": [
    {
      "id": 777,
      "name": "Рога и копыта",
      "url": "https://horns-and-hooves.ru"
    }
  ]
}
```

# Обработка ответа о платеже

```
  from freekassa_ru import Notification
  
  SECRET_KEY_2 = ''
  ip = '0.0.0.0' # IP, с которого пришел запрос
  data = request.GET # или request.POST в зависимости от настроек магазина
  notification = Notification(data=data, secret2=SECRET_KEY_2, ip=ip)
  notification.check() # Проверка IP и подписи
  payment_id = notification.payment_id # получение ID заказа на сайте продавца для изменения статуса оплаты
```

# Обработка ошибок

```
from freekassa_ru import FreekassaError, FreekassaAuthError, FreekassaNotificationError

try:
    fk.get_balance()
except FreekassaError as e:
    print(e) # Ошибка выполнения запроса
except FreekassaAuthError as e:
    print(e) # Ошибка авторизации API
    
try:
    notification.check()
except FreekassaNotificationError as e:
    print(e) # Ошибка проверки оповещения о платеже
```