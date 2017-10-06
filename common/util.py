import constant


def get_symbol(name, base_cur, quote_cur='btc'):
    if name == constant.EX_LQ:
        return "%s_%s" % (base_cur.lower(), quote_cur.lower())
    if name == constant.EX_OKEX:
        return "%s_%s" % (base_cur.lower(), quote_cur.lower())
    if name == constant.EX_BFX:
        base_cur = convert_currency(name, base_cur)
        return "%s%s" % (base_cur.lower(), quote_cur.lower())
    if name == constant.EX_GDAX:
        return "%s-%s" % (base_cur.upper(), quote_cur.upper())
    if name == constant.EX_BINANCE:
        return "%s%s" % (base_cur.upper(), quote_cur.upper())
    if name == constant.EX_CEX:
        return "%s/%s" % (base_cur.upper(), quote_cur.upper())
    if name == constant.EX_EXMO:
        return "%s_%s" % (base_cur.upper(), quote_cur.upper())
    if name == constant.EX_BITTREX:
        return "%s-%s" % (quote_cur.upper(), base_cur.upper())
    return "%s_%s" % (base_cur, quote_cur)


def get_symbol_btc(name, currency):
    return get_symbol(name, base_cur=currency, quote_cur='btc')


def get_symbol_eth(name, currency):
    return get_symbol(name, base_cur=currency, quote_cur='eth')


def convert_currency(name, currency):
    if name == constant.EX_BFX:
        if currency == "dash":
            currency = "dsh"
        if currency == "bcc":
            currency = "bch"
    if name == constant.EX_GDAX:
        currency = currency.upper()
    if name == constant.EX_BINANCE:
        currency = currency.upper()
    if name == constant.EX_CEX:
        currency = currency.upper()
    if name == constant.EX_EXMO:
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

# print (get_symbol_btc(constant.EX_GDAX, u'ETH'))
# print (get_symbol_btc(constant.EX_BINANCE, u'eth'))
