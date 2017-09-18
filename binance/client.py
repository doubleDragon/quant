from decimal import Decimal

import requests

from common import depth

BASE_URL = "https://www.binance.com/api/v1"
TIMEOUT = 5


class PublicClient(object):
    def __init__(self):
        self.url = BASE_URL

    def _url_for(self, path):
        return self.url + "/%s" % path

    def _get(self, url, params=None):
        try:
            resp = requests.get(url=url, timeout=TIMEOUT, params=params)
        except requests.exceptions.RequestException as e:
            print('binance get request failed: ' + str(e))
        else:
            if resp.status_code == requests.codes.ok:
                return resp.json()

    def depth(self, symbol, limit=5):
        url = self._url_for('depth')
        params = {
            'symbol': symbol,
            'limit': limit
        }
        resp = self._get(url=url, params=params)
        if resp is not None:
            data = {
                u'bids': [],
                u'asks': []
            }
            tmp = [u'price', u'amount']

            def fn(x):
                return Decimal(str(x))

            asks = resp[u'asks']
            bids = resp[u'bids']

            for i in range(5):
                # bid is a array
                bid_dict = dict(zip(tmp, bids[i]))
                bid_dict = dict(zip(bid_dict.keys(), map(fn, bid_dict.values())))

                ask_dict = dict(zip(tmp, asks[i]))
                ask_dict = dict(zip(ask_dict.keys(), map(fn, ask_dict.values())))

                data[u'bids'].append(bid_dict)
                data[u'asks'].append(ask_dict)

            return depth.dict_to_depth(data)
