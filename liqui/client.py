#!/usr/bin/python
# -*- coding: UTF-8 -*-
from decimal import Decimal

import requests

from common import depth

PROTOCOL = "https"
HOST = "api.liqui.io/api"
VERSION = "3"

BASE_URL = u"{0:s}://{1:s}/{2:s}".format(PROTOCOL, HOST, VERSION)

# HTTP request timeout in seconds
TIMEOUT = 5.0


def url_for(path, path_arg=None, parameters=None):
    url = "%s/%s" % (BASE_URL, path)
    return url


class PublicClient(object):
    def _get(self, url):
        # return requests.get(url, timeout=TIMEOUT)
        try:
            response = requests.get(url, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            print('OKCoin get' + url + ' failed: ' + str(e))
        else:
            if response.status_code == requests.codes.ok:
                return response.json()

    def depth(self, symbol):
        path = 'depth/%s' % symbol
        resp = self._get(url_for(path))
        if resp is not None:
            data = {
                u'bids': [],
                u'asks': []
            }
            tmp = [u'price', u'amount']

            def fn(x):
                return Decimal(repr(x))

            asks = resp[symbol][u'asks']
            bids = resp[symbol][u'bids']

            for i in range(5):
                # bid is a array
                bid_dict = dict(zip(tmp, bids[i]))
                bid_dict = dict(zip(bid_dict.keys(), map(fn, bid_dict.values())))

                ask_dict = dict(zip(tmp, asks[i]))
                ask_dict = dict(zip(ask_dict.keys(), map(fn, ask_dict.values())))

                data[u'bids'].append(bid_dict)
                data[u'asks'].append(ask_dict)
            return depth.dict_to_depth(data)
