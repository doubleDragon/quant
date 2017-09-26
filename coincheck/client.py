#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import requests

BASE_URL = 'https://coincheck.com/api'


class PublicClient(object):
    def __init__(self):
        super(PublicClient, self).__init__()

    @classmethod
    def url_for(cls, path):
        return "%s/%s" % (BASE_URL, path)

    @classmethod
    def _get(cls, url):
        try:
            resp = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            print("coincheck get %s failed: " % url + str(e))
        else:
            if resp.status_code == requests.codes.ok:
                return resp.json()

    def depth(self):
        url = self.url_for("order_books")
        return self._get(url)
