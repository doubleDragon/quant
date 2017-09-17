#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import sys
# sys.path.append('/root/workspace/python/quant')

import time
from decimal import Decimal

from bitfinex.client import PublicClient as BfxClient
from gdax.client import PublicClient as GdaxClient

from common import constant, util

import logging

logger = logging.getLogger('diff')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('diff_dgax_and_bfx.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

INTERVAL = 3

CURRENCY_LTC = u'ltc'
CURRENCY_ETH = u'eth'
CURRENCY_OMG = u'omg'
CURRENCY_EOS = u'eos'
CURRENCY_DASH = u'dash'

# TRIGGER_LIST = [Decimal('0.00043'), Decimal('0.000095'), Decimal('0.000095'), Decimal('0.000095')]

# DIFF_TRIGGER = Decimal('0.000095')

bfxClient = BfxClient()
gdaxClient = GdaxClient()

DEPTH_INDEX_BFX = 1
DEPTH_INDEX_DGAX = 0

TRIGGER_PERCENT = Decimal('0.7')
is_maker = True

CURRENCIES = [CURRENCY_ETH, CURRENCY_LTC, CURRENCY_OMG, CURRENCY_EOS, CURRENCY_DASH]
trigger_count = {
    CURRENCY_ETH: 0,
    CURRENCY_LTC: 0,
}

D_FORMAT = Decimal('0.00000000')


def get_symbol(ex_name, currency):
    return util.get_symbol_btc(ex_name, currency)


def on_tick():
    for i in range(len(CURRENCIES)):
        currency = CURRENCIES[i]

        depth_dgax = gdaxClient.depth(get_symbol(constant.EX_DGAX, currency))
        if depth_dgax is None:
            return
        depth_bfx = bfxClient.depth(get_symbol(constant.EX_BFX, currency))
        if depth_bfx is None:
            return
        sell_price_lq = depth_dgax.asks[DEPTH_INDEX_DGAX].price
        buy_price_lq = depth_dgax.bids[DEPTH_INDEX_DGAX].price
        buy_price_bfx = depth_bfx.bids[DEPTH_INDEX_BFX].price
        if is_maker:
            diff = buy_price_bfx - buy_price_lq
            diff_percent = diff / buy_price_lq * Decimal('100')
        else:
            diff = buy_price_bfx - sell_price_lq
            diff_percent = diff / sell_price_lq * Decimal('100')
        diff_percent = diff_percent.quantize(D_FORMAT)

        global trigger_count
        logger.debug(str(currency) + '===========>差价:' + str(diff) + "---百分比: " + str(diff_percent) +
                     "---计数: " + str(trigger_count[currency]))

        # trigger = TRIGGER_LIST[i]
        if diff_percent >= TRIGGER_PERCENT:
            trigger_count[currency] += 1


def main():
    while True:
        time.sleep(INTERVAL)
        on_tick()


if __name__ == '__main__':
    main()
