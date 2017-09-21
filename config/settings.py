#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8
from decimal import Decimal

from decouple import config

# 读取所有的key和secret
BFX_API_KEY = config('BFX_API_KEY')
BFX_API_SECRET = config('BFX_API_SECRET')
POLONIEX_API_KEY = config('POLONIEX_API_KEY')
POLONIEX_API_SECRET = config('POLONIEX_API_SECRET')

OKCOIN_API_KEY = config('OKCOIN_API_KEY')
OKCOIN_API_SECRET = config('OKCOIN_API_SECRET')

OKEX_API_KEY = config('OKEX_API_KEY')
OKEX_API_SECRET = config('OKEX_API_SECRET')

LIQUI_API_KEY = config('LIQUI_API_KEY')
LIQUI_API_SECRET = config('LIQUI_API_SECRET')

CEX_API_KEY = config('CEX_API_KEY')
CEX_API_SECRET = config('CEX_API_SECRET')
CEX_USER_ID = "up109027181"

"""主要配置, 根据平台和币种来调整, 改完后记的去调整对应交易所的config"""
# 当前交易币种
CURRENCY = 'dash'
# 单次交易的amount
AMOUNT_ONCE = Decimal('0.01')
# 滑价配置
SLIDE_PRICE = Decimal('0.0000001')
# 差价触发百分比
TRIGGER_DIFF_PERCENT = Decimal('0.8')
# 吃单时，max_amount的几分之一
AMOUNT_RATE = Decimal('2')
# 账户内保留的法币stock, 可能是btc的数量，也可能是margin钱包usd数量，取决于交易所, 先设置成0
AMOUNT_RETAIN = Decimal('0')

"""其他配置, 基本不变, 不需要动"""
INTERVAL = 0.5
TICK_INTERVAL = 1
MAX_DELAY = Decimal('3000')
