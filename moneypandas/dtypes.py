import re
# from .parser import _currency_symbol
import numpy as np
import iso4217parse


def find_currency_data():
    print("running funct")
    currency_symbols = iso4217parse._symbols()
    symbols = []
    for item in currency_symbols:
        code = iso4217parse.parse(item[0])
        symbols.append({'currency': code[0][0], 'symbol': item[0]})
    return symbols

symbols = find_currency_data()

money_patterns = [(re.compile(r[0]), r[1]) for r in [
    (
        r'(-?)([' + ''.join(find_currency_data()) + r'])(\d*\.?\d*\d)',       # -£123.00
        lambda m: (np.float64(m.group(1) + m.group(3)), symbols[m.group(2)])
    ),
    (
        r'([A-Z]{3})\s*(-?\d*\.?\d*\d)',                         # EUR 123
        lambda m: (np.float64(m.group(2)), m.group(1))
    ),
    (
        r'(-?\d*\.?\d*\d)\s*([A-Z]{3})',                         # 97GBP
        lambda m: (np.float64(m.group(1)), m.group(2))
    ),
]]

def is_money(value):
    # TODO: Better detection
    if isinstance(value, str):
        return any([r[0].match(value) for r in money_patterns])
    elif isinstance(value, bytes):
        pass
    elif isinstance(value, int):
        return True
    else:
        return False

