import constant


def get_symbol_btc(name, currency):
    if name == constant.EX_LQ:
        return "%s_btc" % currency
    if name == constant.EX_OKEX:
        return "%s_btc" % currency
    if name == constant.EX_BFX:
        return "%sbtc" % convert_currency(constant.EX_BFX, currency)
    if name == constant.EX_DGAX:
        return "%s-BTC" % convert_currency(constant.EX_DGAX, currency)
    if name == constant.EX_BINANCE:
        return "%sBTC" % convert_currency(constant.EX_BINANCE, currency)
    return currency


def get_symbol_eth(name, currency):
    if name == constant.EX_LQ:
        return "%s_eth" % currency
    if name == constant.EX_OKEX:
        return "%s_eth" % currency
    if name == constant.EX_BFX:
        return "%seth" % convert_currency(constant.EX_BFX, currency)
    return currency


def convert_currency(name, currency):
    if name == constant.EX_BFX:
        if currency == "dash":
            currency = "dsh"
    if name == constant.EX_DGAX:
        currency = currency.upper()
    if name == constant.EX_BINANCE:
        currency = currency.upper()
    return currency

# print (get_symbol(constant.EX_OKEX, u'ltc'))
# print (get_symbol(constant.EX_LQ, u'ltc'))
# print (get_symbol(constant.EX_BFX, u'ltc'))
#
# print (get_symbol(constant.EX_OKEX, u'eth'))
# print (get_symbol(constant.EX_LQ, u'eth'))
# print (get_symbol(constant.EX_BFX, u'eth'))
# print (get_symbol_btc(constant.EX_BFX, u'dash'))
# print (get_symbol_btc(constant.EX_LQ, u'dash'))

# print (get_symbol_btc(constant.EX_DGAX, u'ETH'))
# print (get_symbol_btc(constant.EX_BINANCE, u'eth'))
