#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bitfinex.client import PrivateClient as BfxClient

from config import settings

API_KEY = settings.BFX_API_KEY
API_SECRET = settings.BFX_API_SECRET

client = BfxClient(API_KEY, API_SECRET)
# print(client.symbols())

# balance
# print (client.balance())

# ticker
# print(client.ticker('ltcusd'))

# depth
print(client.depth('dashbtc'))


# trade
# symbol = 'eosusd'
# amount = '0.1'
# price = '5.0'
# # order_type = 'exchange limit'
# order_type = 'exchange limit'
#
# result = client.sell(symbol=symbol, amount=amount, price=price)
# if result.error is None:
#     print(str(result.order_id))
# else:
#     print(str(result.error))


# cancel order,  order id 必须是整数，类型为int
# print(client.cancel_order(3798555555))


# get order,  order id 必须是整数，类型为int
# r_order = client.get_order(3798555555)
# if r_order.is_closed():
#     print("%s is closed" % r_order.order_id)
# else:
#     if r_order.is_canceled():
#         print("%s is canceled" % r_order.order_id)
#     else:
#         print("%s is pending" % r_order.order_id)
