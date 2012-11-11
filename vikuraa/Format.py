import locale

CurrencySymbol = 'Rf'

def Currency(value, grouping=False, symbol=CurrencySymbol):
    curr = locale.currency(value, grouping=grouping, symbol=False)
    return symbol + curr