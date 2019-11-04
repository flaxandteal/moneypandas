import re
import numpy as np
from decimal import Decimal

symbols = {
        '£': 'GBP',
        '$': 'USD',
        '€': 'EUR',
        '¥': 'JPY',
        '₹': 'INR'
}
money_patterns = [(re.compile(r[0]), r[1]) for r in [
    (
        r'(-?)([' + ''.join(symbols) + r'])(\d*\.?\d*\d)',       # -£123.00
        lambda m: (Decimal(m.group(1) + m.group(3)), symbols[m.group(2)])
    ),
    (
        r'([A-Z]{3})\s*(-?\d*\.?\d*\d)',                         # EUR 123
        lambda m: (Decimal(m.group(2)), m.group(1))
    ),
    (
        r'(-?\d*\.?\d*\d)\s*([A-Z]{3})',                         # 97GBP
        lambda m: (Decimal(m.group(1)), m.group(2))
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
