#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class HttpError(object):

    def __init__(self, code=-10000, message='unknown error'):
        super(HttpError, self).__init__()
        self.code = code
        self.message = message

    def __repr__(self):
        data = {
            u'code': self.code,
            u'message': self.message,
        }
        return str(data)

    def __str__(self):
        data = {
            u'code': self.code,
            u'message': self.message,
        }
        return str(data)
