#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import sys
# sys.path.append('/root/workspace/python/quant')

import time
from decimal import Decimal

from bitfinex.client import PrivateClient as BfxClient
from config import settings
from liqui.client import PublicClient as LiquiClient

from common import constant, util

import logging

logger = logging.getLogger('diff')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('diff.log')
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

# TRIGGER_LIST = [Decimal('0.00043'), Decimal('0.000095'), Decimal('0.000095'), Decimal('0.000095')]

# DIFF_TRIGGER = Decimal('0.000095')

bfxClient = BfxClient(settings.BFX_API_KEY, settings.BFX_API_SECRET)
lqClient = LiquiClient()

DEPTH_INDEX_BFX = 1
DEPTH_INDEX_LQ = 0

TRIGGER_PERCENT = Decimal('0.7')

CURRENCIES = [CURRENCY_ETH, CURRENCY_LTC, CURRENCY_OMG, CURRENCY_EOS]
trigger_count = {
    CURRENCY_ETH: 0,
    CURRENCY_LTC: 0,
    CURRENCY_OMG: 0,
    CURRENCY_EOS: 0
}
is_eth = False
# CURRENCIES = [CURRENCY_OMG, CURRENCY_EOS]
# trigger_count = {
#     CURRENCY_OMG: 0,
#     CURRENCY_EOS: 0
# }

D_FORMAT = Decimal('0.00000000')


def get_symbol(ex_name, currency):
    if is_eth is True:
        return util.get_symbol_eth(ex_name, currency)
    else:
        return util.get_symbol_btc(ex_name, currency)


def on_tick():
    for i in range(len(CURRENCIES)):
        currency = CURRENCIES[i]

        depth_lq = lqClient.depth(get_symbol(constant.EX_LQ, currency))
        if depth_lq is None:
            return
        depth_bfx = bfxClient.depth(get_symbol(constant.EX_BFX, currency))
        if depth_bfx is None:
            return
        sell_price_lq = depth_lq.asks[DEPTH_INDEX_LQ].price
        buy_price_bfx = depth_bfx.bids[DEPTH_INDEX_BFX].price
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
