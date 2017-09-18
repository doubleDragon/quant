#!/usr/bin/python
# -*- coding: UTF-8 -*-

from binance.client import PublicClient
from common import util, constant

currency = 'eth'

client = PublicClient()
# depth
print (client.depth(util.get_symbol_btc(constant.EX_BINANCE, currency)))
