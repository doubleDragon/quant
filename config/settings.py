#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8
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

"""http request timeout"""
TIMEOUT = 5
