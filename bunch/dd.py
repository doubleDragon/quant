#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bunch import Bunch

if __name__ == '__main__':
    a = Bunch({
        'x': 1
    })
    if a.x is None:
        print('x propery is null')
    else:
        print('x propery is not null')

    if 'y' not in a.keys() or a.y is None:
        print('y propery is null')
    else:
        print('y propery is not null')
