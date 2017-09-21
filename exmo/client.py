#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from decimal import Decimal

import requests

from common import depth

BASE_URL = 'https://api.exmo.com/v1'


class PublicClient(object):
    def __init__(self):
        super(PublicClient, self).__init__()

    @classmethod
    def _build_parameters(cls, parameters):
        # sort the keys so we can test easily in Python 3.3 (dicts are not
        # ordered)
        keys = list(parameters.keys())
        keys.sort()

        return '&'.join(["%s=%s" % (k, parameters[k]) for k in keys])

    def url_for(self, path, parameters=None):
        # build the basic url
        url = "%s/%s" % (BASE_URL, path)

        # Append any parameters to the URL.
        if parameters:
            url = "%s?%s" % (url, self._build_parameters(parameters))

        return url

    @classmethod
    def _get(cls, url):
        try:
            resp = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            print("exmo get %s failed: " % url + str(e))
        else:
            if resp.status_code == requests.codes.ok:
                return resp.json()

    def depth(self, symbol):
        params = {
            'pair': symbol,
            'limit': 5
        }
        url = self.url_for('order_book/', params)
        resp = self._get(url)
        if resp is not None:
            resp = resp.values()[0]

            data = {
                u'bids': [],
                u'asks': []
            }

            def fn(x):
                return Decimal(str(x))

            tmp = [u'price', u'amount']

            for i in range(5):
                # bid is a array
                bid_dict = dict(zip(tmp, resp[u'bid'][i]))
                bid_dict = dict(zip(bid_dict.keys(), map(fn, bid_dict.values())))

                ask_dict = dict(zip(tmp, resp[u'ask'][i]))
                ask_dict = dict(zip(ask_dict.keys(), map(fn, ask_dict.values())))

                data[u'bids'].append(bid_dict)
                data[u'asks'].append(ask_dict)

            return depth.dict_to_depth(data)
