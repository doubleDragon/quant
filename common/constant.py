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
EX_GDAX = 'gdax'
EX_BINANCE = 'binance'
EX_CEX = 'cex'
EX_EXMO = 'exmo'
EX_CHECK = 'coincheck'
EX_POLONIEX = 'poloniex'
EX_BITTREX = 'bittrex'

EX_SET = (
    EX_OKEX,
    EX_BFX,
    EX_LQ,
    EX_GDAX,
    EX_BINANCE,
    EX_CEX,
    EX_EXMO,
    EX_CHECK,
    EX_POLONIEX,
    EX_BITTREX,
)

"""
lq 要用到的错误码
832: 卖的时候币不够了
831: 买的时候btc不够了
"""
CODE_LQ_SELL_NOT_ENOUGH = 832
CODE_LQ_BUY_NOT_ENOUGH = 831
