#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from decimal import Decimal

import requests
from config import settings
from common import depth

BASE_URL = 'https://cex.io/api'


class PublicClient(object):
    def __init__(self):
        self.url = BASE_URL

    def _get(self, url, params=None):
        try:
            resp = requests.get(url=url, params=params, timeout=settings.TIMEOUT)
        except requests.exceptions.RequestException as e:
            print('cex get failed: ' + str(e))
        else:
            if resp.status_code == requests.codes.ok:
                return resp.json()

    def depth(self, symbol):
        """
        api返回的ask是降序排列，需要转换一下
        {
            "timestamp":1505833871,
            "bids":[
                [0.07242200,0.17000000],
                [0.07232997,61.80311400]
            ],
            "asks":[
                [0.07259999,0.10000000],
                [0.07260000,0.30519200]
            ],
            "pair":"ETH:BTC",
            "id":79460657,
            "sell_total":"9719.80191000",
            "buy_total":"563.31321512"
        }
        """
        url = self.url + ("/order_book/%s/" % symbol)
        params = {
            'depth': 5
        }
        resp = self._get(url=url, params=params)
        if resp is not None:
            data = {
                u'bids': [],
                u'asks': []
            }
            tmp = [u'price', u'amount']

            def fn(x):
                return Decimal(repr(x))

            # sort the bids and asks
            resp[u'asks'] = sorted(resp[u'asks'], key=lambda ask_item: ask_item[0])

            for i in range(5):
                # bid is a array
                bid_dict = dict(zip(tmp, resp[u'bids'][i]))
                bid_dict = dict(zip(bid_dict.keys(), map(fn, bid_dict.values())))

                ask_dict = dict(zip(tmp, resp[u'asks'][i]))
                ask_dict = dict(zip(ask_dict.keys(), map(fn, ask_dict.values())))

                data[u'bids'].append(bid_dict)
                data[u'asks'].append(ask_dict)

            return depth.dict_to_depth(data)
