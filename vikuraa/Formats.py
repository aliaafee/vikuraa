import locale

def CurrencyFormat(self, value, symbol='Rf'):
    curr = locale.currency(value, grouping=True, symbol=False)
    return symbol + curr