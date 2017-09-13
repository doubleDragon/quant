#!/usr/bin/python
# -*- coding: UTF-8 -*-


from okex.client import PrivateClient as OkexClient

from config import settings

API_KEY = settings.OKEX_API_KEY
API_SECRET = settings.OKEX_API_SECRET

client = OkexClient(API_KEY, API_SECRET)
# print('ticker--------->' + str(client.ticker('ltc_btc')))
# print('depth--------->' + str(client.depth('ltc_btc')))

# print('balance------->' + str(client.balance()))

# orider_id = client.buy('ltc_btc', '0.0160', 0.1)
# print ('order_id: ' + str(orider_id))
