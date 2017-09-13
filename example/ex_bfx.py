#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bitfinex.client import PrivateClient as BfxClient

from config import settings

API_KEY = settings.BFX_API_KEY
API_SECRET = settings.BFX_API_SECRET

client = BfxClient(API_KEY, API_SECRET)
# print(client.symbols())
print (client.balance('ltc'))
# print(client.ticker('ltcusd'))
# print(client.depth('ltcusd'))

# symbol = 'eosusd'
# amount = '0.1'
# price = '5.0'
# side = 'sell'
# order_type = 'exchange limit'
#
# order_id = client.place_order(amount=amount, price=price, side=side, ord_type=order_type,
#                               symbol=symbol)
#
# print('order id: ' + str(order_id))
