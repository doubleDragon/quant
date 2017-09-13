#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys  
sys.path.append('/root/workspace/python/quant')  

import time
from decimal import Decimal

from bitfinex.client import PrivateClient as BfxClient
from config import settings
from liqui.client import PublicClient as LiquiClient

from common import constant, util


INTERVAL = 3

CURRENCY_LTC = u'ltc'
CURRENCY_ETH = u'eth'
CURRENCY_OMG = u'omg'
CURRENCY_EOS = u'eos'

CURRENCIES = [CURRENCY_ETH, CURRENCY_LTC, CURRENCY_OMG, CURRENCY_EOS]
TRIGGER_LIST = [Decimal('0.00043'), Decimal('0.000095'), Decimal('0.000095'), Decimal('0.000095')]

# DIFF_TRIGGER = Decimal('0.000095')

bfxClient = BfxClient(settings.BFX_API_KEY, settings.BFX_API_SECRET)
lqClient = LiquiClient()

DEPTH_INDEX_BFX = 1
DEPTH_INDEX_LQ = 0

trigger_count = {
    CURRENCY_ETH: 0,
    CURRENCY_LTC: 105,
    CURRENCY_OMG: 0,
    CURRENCY_EOS: 0
}


def on_tick():
    for i in range(len(CURRENCIES)):
        currency = CURRENCIES[i]

        depth_lq = lqClient.depth(util.get_symbol(constant.EX_LQ, currency))
        if depth_lq is None:
            return
        depth_bfx = bfxClient.depth(util.get_symbol(constant.EX_BFX, currency))
        if depth_bfx is None:
            return
        sell_price_lq = depth_lq.asks[DEPTH_INDEX_LQ].price
        buy_price_bfx = depth_bfx.bids[DEPTH_INDEX_BFX].price
        diff = buy_price_bfx - sell_price_lq

        global trigger_count
        print(str(currency) + '差价===========>diff:' + str(diff) + "---count: " + str(trigger_count[currency]))

        trigger = TRIGGER_LIST[i]
        if diff >= trigger:
            trigger_count[currency] += 1


def main():
    while True:
        time.sleep(INTERVAL)
        on_tick()


if __name__ == '__main__':
    main()
