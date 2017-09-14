from decimal import Decimal

from config import settings
from liqui.client import PrivateClient as Client

client = Client(settings.LIQUI_API_KEY, settings.LIQUI_API_SECRET)

# balance, lq just btc
# print(client.balance())

# buy or sell
# result = client.sell('ltc_btc', Decimal('0.015744'), 0.1)
# result = client.buy('ltc_btc', Decimal('0.01501000'), 0.1)
# if result.error is None:
#     print(str(result.order_id))
# else:
#     print(str(result.error))

# if result.code == 831:
#     print('lq btc not enough to buy, code is 831')
# if result.code == 832:
#     print('lq btc not enough to sell, code is 832')


# get order info
r_order = client.get_order(63613389)
if r_order is not None:
    print("%s status is %s" % (r_order.order_id,r_order.status))
    if r_order.is_closed():
        print("%s is closed" % r_order.order_id)
    else:
        if r_order.is_canceled():
            print("%s is canceled" % r_order.order_id)
        else:
            print("%s is pending" % r_order.order_id)
else:
    order_id = 63613389
    print("%d order info failed" % order_id)

# cancel
print(client.cancel_order(63613389))
