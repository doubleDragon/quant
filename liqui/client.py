#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import hmac
import urllib
from decimal import Decimal
from urllib import urlencode

import requests
import time

from common import depth

PROTOCOL = "https"
HOST = "api.liqui.io/api"
VERSION = "3"

BASE_URL = u"{0:s}://{1:s}/{2:s}".format(PROTOCOL, HOST, VERSION)

# HTTP request timeout in seconds
TIMEOUT = 5.0


class LiquiApiError(Exception):
    pass


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


class PrivateClient(PublicClient):
    def __init__(self, api_key, api_secret):
        PublicClient.__init__(self)
        self._api_key = api_key
        self._api_secret = api_secret

    @property
    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return int(time.time())
        # return str(int(round(time.time() * 10000)))

    def __sign(self, params):
        sig = hmac.new(self._api_secret.encode(), params.encode(), hashlib.sha512)
        return sig.hexdigest()

    def _post(self, method, params):
        params['method'] = method
        params['nonce'] = str(self._nonce)
        params = urlencode(params)

        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Key": self._api_key,
                   "Sign": self.__sign(params)}
        try:
            resp = requests.post('https://api.liqui.io/tapi', data=params, headers=headers)
        except requests.exceptions.RequestException as e:
            print('liqui post' + ' failed: ' + str(e))
        else:
            if resp.status_code == requests.codes.ok:
                return resp.json()

    def _get_info(self):
        """
        need to parse and convert to account object
        :return:
        """
        return self._post('getInfo', {})

    def balance(self):
        return self._get_info()

    # def balances(self):
    #     """
    #     Just return btc coins, may be need another coin
    #     """
    #     resp = self.get_info()
    #     if resp is not None:
    #         return resp['funds']['btc']
