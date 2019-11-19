# pylint: disable = invalid-name
""" Methods to parse strings/datatypes to find currencies """
import numpy as np
from pandas.api.types import is_list_like
import money
from .dtypes import money_patterns


def to_money(values, default_money_code=None):
    """Convert values to MoneyArray

    Parameters
    ----------
    values : int, str, bytes, or sequence of those

    Returns
    -------
    addresses : MoneyArray

    Examples
    --------
    Parse strings
    >>> to_money(['£128',
    ...               '129 EUR'])
    <MoneyArray(['128 GBP', '129 EUR'])>

    Or integers
    >>> to_money([128, 131], default_money_code='GBP')
    <MoneyArray(['128 GBP', '131 GBP'])>
    """
    from . import MoneyArray

    if not is_list_like(values):
        values = [values]

    values, default_money_code = _to_money_array(
        values, default_money_code=default_money_code)
    return MoneyArray(
        values,
        default_money_code=default_money_code
    )


def _to_money_array(values, default_money_code=None):
    """ Method to convert a money object to a money array """
    from .money_array import MoneyType, MoneyArray

    if isinstance(values, MoneyArray):
        if values.default_money_code:
            default_money_code = default_money_code
        return values.data, default_money_code

    values = [_as_money_object(v, default_money_code) for v in values]

    return np.atleast_1d(np.asarray(values, dtype=MoneyType._record_type)), default_money_code

def _as_money_object(val, default_money_code=None):
    """ Method to return a tuple with the monetary value
    and the currency. Attempt to parse 'val' as any Money object.
    Uses regex (money_patterns) to get the amount & the currency.
    'cu' represents currency, and 'va' represents value.
    """

    cu, va = None, None

    if isinstance(val, np.void):
        cu = val['cu']
        va = val['va']
    elif val in (None, '', np.nan):
        cu = ''
        va = 0
    elif isinstance(val, money.Money):
        cu = val.currency
        va = np.float64(val.amount)
    elif isinstance(val, str):
        for r, extract in money_patterns:
            m = r.match(val)
            if m:
                # calls a lambda function that gets the value that matches the expressions
                va, cu = extract(m)

    elif is_list_like(val) and len(val) == 2:
        try:
            va = np.float64(val[0])
            cu = str(val[1])
        except TypeError:
            pass

    if cu is not None and va is not None:
        return va, cu

    try:
        va = np.float64(val)
    except TypeError:
        pass
    else:
        if default_money_code:
            cu = default_money_code
            return va, cu
        else:
            raise ValueError(
                "Currency code is unavailable - cannot convert {}. Set a default?".format(val))

    raise ValueError("Could not parse {} as money".format(val))
