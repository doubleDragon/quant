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


# cancel
# print(client.cancel_order('63408509'))
