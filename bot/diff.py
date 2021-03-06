#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
from decimal import Decimal

from bitfinex.client import PublicClient as BfxClient
from liqui.client import PublicClient as LiquiClient

from common import constant, util, log

import logging

logger = log.get_logger(log_name='diff', level=logging.DEBUG)

INTERVAL = 3

CURRENCY_LTC = u'ltc'
CURRENCY_ETH = u'eth'
CURRENCY_OMG = u'omg'
CURRENCY_EOS = u'eos'
CURRENCY_DASH = u'dash'
CURRENCY_BCC = u'bcc'

# TRIGGER_LIST = [Decimal('0.00043'), Decimal('0.000095'), Decimal('0.000095'), Decimal('0.000095')]

# DIFF_TRIGGER = Decimal('0.000095')

bfxClient = BfxClient()
lqClient = LiquiClient()

DEPTH_INDEX_BFX = 1
DEPTH_INDEX_LQ = 0

TRIGGER_PERCENT = Decimal('1.0')

CURRENCIES = [CURRENCY_ETH, CURRENCY_LTC, CURRENCY_OMG, CURRENCY_EOS, CURRENCY_DASH, CURRENCY_BCC]
trigger_count = {
    CURRENCY_ETH: 0,
    CURRENCY_LTC: 0,
    CURRENCY_OMG: 0,
    CURRENCY_EOS: 0,
    CURRENCY_DASH: 0,
    CURRENCY_BCC: 0
}
is_maker = False
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
        buy_price_lq = depth_lq.asks[DEPTH_INDEX_LQ].price
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
