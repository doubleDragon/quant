#!/usr/bin/python
# -*- coding: UTF-8 -*-

from common import util, constant
from gdax.client import PublicClient as Client

client = Client()
currency = 'eth'

# symbols
# print(client.get_products())

# ticker
print (client.ticker(util.get_symbol_btc(constant.EX_DGAX, currency)))

# depth
# print(client.depth(product_id=util.get_symbol_btc(constant.EX_DGAX, currency), level=2))
