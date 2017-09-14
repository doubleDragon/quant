import constant


def get_symbol_btc(name, currency):
    if name == constant.EX_LQ:
        return "%s_btc" % currency
    if name == constant.EX_OKEX:
        return "%s_btc" % currency
    if name == constant.EX_BFX:
        return "%sbtc" % currency
    return currency


def get_symbol_eth(name, currency):
    if name == constant.EX_LQ:
        return "%s_eth" % currency
    if name == constant.EX_OKEX:
        return "%s_eth" % currency
    if name == constant.EX_BFX:
        return "%seth" % currency
    return currency

# print (get_symbol(constant.EX_OKEX, u'ltc'))
# print (get_symbol(constant.EX_LQ, u'ltc'))
# print (get_symbol(constant.EX_BFX, u'ltc'))
#
# print (get_symbol(constant.EX_OKEX, u'eth'))
# print (get_symbol(constant.EX_LQ, u'eth'))
# print (get_symbol(constant.EX_BFX, u'eth'))
