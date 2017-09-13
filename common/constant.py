# coding=utf-8

"""
ORDER_STATE_PENDING	:未完成
ORDER_STATE_CLOSED	:已关闭
ORDER_STATE_CANCELED:已取消


ticker数据结构如下:
{
    sell: 0.5,
    buy: 0.5,
    last: 0.5
}
"""

ORDER_STATE_PENDING = 1
ORDER_STATE_CLOSED = 2
ORDER_STATE_CANCELED = 4

EX_OKEX = 'okex'
EX_BFX = 'bitfinex'
EX_LQ = 'liqui'


