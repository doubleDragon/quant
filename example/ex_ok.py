#!/usr/bin/python
# -*- coding: UTF-8 -*-


from okcoin.client import PrivateClient as OkClient

from config import settings

API_KEY = settings.OKCOIN_API_KEY
API_SECRET = settings.OKCOIN_API_SECRET

client = OkClient(API_KEY, API_SECRET)
print('ticker--------->' + str(client.ticker('ltc_cny')))
print('depth--------->' + str(client.depth('btc_cny')))

print('account------->' + str(client.account()))
