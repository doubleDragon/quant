#!/usr/bin/python
# -*- coding: UTF-8 -*-


from poloniex.client import Client as PoloniexClient
from config import settings

API_KEY = settings.POLONIEX_API_KEY
API_SECRET = settings.POLONIEX_API_SECRET

p = PoloniexClient(API_KEY, API_SECRET)
# # print(p.ticker('ltc'))
# # print(p.depth('btc_ltc'))
# print (p.buy('BTC_XMR', 0.0201, 0.1))

# print (p.view_active_orders('BTC_XMR'))
# print (p.view_margin_position('BTC_XMR'))
print (p.margin_sell(symbol='BTC_XMR', rate=0.026750, amount=1))
