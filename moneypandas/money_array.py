import abc
import decimal
import collections

import numpy as np
from decimal import Decimal
from pandas.compat.numpy import function as nv
import pandas as pd
from pandas.core import nanops
import money
from pandas.api.extensions import ExtensionDtype

from ._accessor import (DelegatedMethod, DelegatedProperty,
                        delegated_method)
from .base import NumPyBackedExtensionArrayMixin
from .parser import _as_money_object
import re

# -----------------------------------------------------------------------------
# Extension Type
# -----------------------------------------------------------------------------

@pd.api.extensions.register_extension_dtype
class MoneyType(ExtensionDtype):
    name = 'money'
    na_value = np.nan
    type = money.XMoney
    kind = 'O'
    default_money_code = None
    _record_type = np.dtype([('va', Decimal), ('cu', 'U3')])
    _record_na_value = (0, '')

    def __init__(self, *args, default_money_code=None, **kwargs):
        self.default_money_code = default_money_code

        super(MoneyType, self).__init__(*args, **kwargs)

    @classmethod
    def construct_from_string(cls, string):
        if string == cls.name:
            return cls()
        else:
            match = re.match(cls.name + r'\[([A-Z]{3})\]', string)

            if match:
                default_money_code = match.group(0)
                return cls(default_money_code=default_money_code)

            raise TypeError("Cannot construct a '{}' from "
                            "'{}'".format(cls, string))

    @classmethod
    def construct_array_type(cls):
        return MoneyArray


# -----------------------------------------------------------------------------
# Extension Container
# -----------------------------------------------------------------------------


class MoneyArray(NumPyBackedExtensionArrayMixin):
    """Holder for Money Amounts.

    MoneyArray is a container for Money Amounts. It satisfies pandas'
    extension array interface, and so can be stored inside
    :class:`pandas.Series` and :class:`pandas.DataFrame`.

    See :ref:`usage` for more.
    """
    __array_priority__ = 1000
    _dtype = MoneyType()
    _itemsize = 20
    ndim = 1
    can_hold_na = True
    default_money_code = None

    def __init__(self, values, default_money_code=None, dtype=None, copy=False):
        from .parser import _to_money_array

        # TODO: copy
        if dtype and dtype != self.dtype:
            raise TypeError("Can only construct MoneyArray with underlying (f64, U3) not {}".format(dtype))

        values, self.default_money_code = _to_money_array(values, default_money_code=default_money_code)  # TODO: avoid potential copy
        # TODO: dtype?
        if copy:
            values = values.copy()
        self.data = values

    def to_decimals(self, money_code=None):
        r"""Create a list of decimals from an ISO4712 code, attempting conversion with XMoney where necessary.

        Parameters
        ----------
        money_code : ISO4712 3-letter currency code

        Returns
        -------
        list of decimals

        Examples
        --------
        >>> arr = MoneyArray([10, 20], 'GBP')
        >>> values = arr.to_decimals('GBP')
        >>> values
        [10, 20]

        See Also
        --------
        to_bytes
        """

        if not money_code:
            money_code = self.default_money_code
            if not money_code:
                codes = {c['cu'] for c in self.data if c['cu']}
                if len(codes) != 1:
                    raise TypeError("Cannot output mixed-currency monies as decimal "
                        "without either a target or default currency")
                money_code = codes[0]

        mask = self.isna()
        same = (self.data['cu'] == money_code) | mask
        decimalize = np.vectorize(decimal.Decimal)
        result = decimalize(self.data['va'])
        for i, ceq in enumerate(same):
            if not ceq:
                result[i] = money.XMoney(*self.data[i]).to(money_code).amount

        return result

    # Operations thanks to pandas.core.arrays.base.numpy_
    def _min(self, ndarray, axis=None, out=None, keepdims=False, skipna=True):
        nv.validate_min((), dict(out=out, keepdims=keepdims))
        return nanops.nanmin(ndarray, axis=axis, skipna=skipna)

    def _max(self, ndarray, axis=None, out=None, keepdims=False, skipna=True):
        nv.validate_max((), dict(out=out, keepdims=keepdims))
        return nanops.nanmax(ndarray, axis=axis, skipna=skipna)

    def _sum(
        self,
        ndarray,
        axis=None,
        dtype=None,
        out=None,
        keepdims=False,
        initial=None,
        skipna=True,
        min_count=0,
    ):
        nv.validate_sum(
            (), dict(dtype=dtype, out=out, keepdims=keepdims, initial=initial)
        )
        return nanops.nansum(
            ndarray, axis=axis, skipna=skipna, min_count=min_count
        )

    def _reduce(self, name, skipna=True, **kwargs):
        """ _reduce is called when min, sum or max is called via the pandas series (column). 
        It's stored as an array of floats & the _reduce operation is performed on that.
        """
        currencies = [cu for cu in np.unique(self.data['cu']) if cu]
        totals = {}

        if name == 'mean':
            meth = getattr(self, '_sum', None)
        else:
            meth = getattr(self, '_' + name, None)

        if meth:
            if len(currencies) > 1:
                money_code = self.default_money_code if self.default_money_code else currencies[0]
                for i, currency in enumerate(currencies):
                    totals[currency] = money.XMoney(
                        meth(self.data['va'][self.data['cu'] == currency], skipna=skipna, **kwargs),
                        currency
                    )
                total = meth(
                    np.array([subtotal.to(money_code).amount for subtotal in totals.values()]),
                    skipna=skipna,
                    **kwargs
                )
                if name == 'mean':
                    total = total / len(self.data)
                total = money.XMoney(amount=total, currency=money_code)
            else:
                money_code = currencies[0] if currencies else self.default_money_code
                total = money.XMoney(meth(self.data['va'], skipna=skipna, **kwargs), money_code)

            return total
        else:
            msg = "'{}' does not implement reduction '{}'"
            raise TypeError(msg.format(type(self).__name__, name))

    @classmethod
    def from_bytes(cls, bytestring):
        r"""Create a MoneyArray from a bytestring.

        Parameters
        ----------
        bytestring : bytes
            Note that bytestring is a Python 3-style string of bytes

        Returns
        -------
        MoneyArray

        Examples
        --------
        >>> arr = MoneyArray([10, 20])
        >>> buf = arr.to_bytes()
        >>> buf
        b'\x00\x00\...x00\x02'
        >>> MoneyArray.from_bytes(buf)
        MoneyArray(['10GBP', '10GBP'])

        See Also
        --------
        to_bytes
        """
        data = np.frombuffer(bytestring, dtype=MoneyType._record_type)
        return cls._from_ndarray(data)

    @classmethod
    def _from_ndarray(cls, data, copy=False):
        """Zero-copy construction of an MoneyArray from an ndarray.

        Parameters
        ----------
        data : ndarray
            This should have MoneyType._record_type dtype
        copy : bool, default False
            Whether to copy the data.

        Returns
        -------
        ExtensionArray
        """
        if copy:
            data = data.copy()
        new = MoneyArray([])
        new.data = data
        return new

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    # With thanks to the pandas docs
    def take(self, indices, allow_fill=False, fill_value=None):
        from pandas.core.algorithms import take

        if allow_fill and fill_value is None:
            fill_value = self.dtype.na_value

        if fill_value is self.dtype.na_value:
            fill_value = self.dtype._record_na_value

        # fill value should always be translated from the scalar
        # type for the array, to the physical storage type for
        # the data, before passing to take.

        indices = np.asarray(indices)
        if allow_fill:
            mask = (indices == -1)
            if not len(self):
                if not (indices == -1).all():
                    msg = "Invalid take for empty array. Must be all -1."
                    raise IndexError(msg)
                else:
                    # all NA take from and empty array
                    result = np.zeros(len(indices), dtype=self.dtype._record_type)
                    result.fill(fill_value)
                    return self._from_ndarray(result)
            if (np.asarray(indices) < -1).any():
                msg = ("Invalid value in 'indices'. Must be all >= -1 "
                       "for 'allow_fill=True'")
                raise ValueError(msg)

        result = take(self.data, indices, allow_fill=False)

        if allow_fill:
            result[mask] = fill_value

        return self._from_sequence(result, dtype=self.dtype, default_money_code=self.default_money_code)


    @classmethod
    def _from_sequence(cls, scalars, dtype=None, copy=False, default_money_code=None):
        return cls(scalars, dtype=dtype, copy=copy, default_money_code=default_money_code)

    @classmethod
    def _from_sequence_of_strings(cls, strings, dtype=None, copy=False, default_money_code=None):
        return cls(strings, dtype=dtype, copy=copy, default_money_code=default_money_code)

    def isna(self):
        return self.data['cu'] == ''

    # -------------------------------------------------------------------------
    # Interfaces
    # -------------------------------------------------------------------------

    def __repr__(self):
        rep = super(MoneyArray, self).__repr__()

        money_code = self.default_money_code
        if money_code:
            class_name = self.__class__.__name__
            rep = rep.replace(class_name, f"{class_name}[{money_code}]")

        return rep

    @staticmethod
    def _box_scalar(scalar):
        if scalar == (0, ''):
            return np.nan
        elif type(scalar) is tuple:
            return money.XMoney(scalar[0], scalar[1])
        return money.XMoney(scalar['va'], scalar['cu'])

    @property
    def _parser(self):
        from .parser import to_money
        return lambda val: to_money(val, default_money_code=self.default_money_code)

    def __setitem__(self, key, value):
        from .parser import to_money

        value = to_money(value, default_money_code=self.default_money_code).data
        self.data[key] = value

    def __iter__(self):
        return iter(self.to_pymoney())

    # ------------------------------------------------------------------------
    # Serializaiton / Export
    # ------------------------------------------------------------------------

    def to_pymoney(self):
        """Convert the array to a list of scalar Money objects.

        Returns
        -------
        addresses : List
            Each element of the list will be a :class:`money.XMoney` or np.nan

        See Also
        --------

        Examples
        ---------
        >>> MoneyArray(['120 EUR', '127 USD']).to_pymoney()
        [XMoney('120', 'EUR'), XMoney('127', 'USD')]
        """
        return [money.XMoney(x['va'], x['cu']) if x['cu'] else np.nan for x in self.data]

    def to_bytes(self):
        r"""Serialize the MoneyArray as a Python bytestring.

        This and :meth:MoneyArray.from_bytes is the fastest way to roundtrip
        serialize and de-serialize a MoneyArray.

        See Also
        --------
        MoneyArray.from_bytes

        Examples
        --------
        >>> arr = MoneyArray('GBP', [10, 20])
        >>> arr.to_bytes()
        b'\x00\x00\...x00\x02'
        """
        return self.data.tobytes()

    def astype(self, dtype, copy=True):
        if isinstance(dtype, MoneyType):
            if copy:
                self = self.copy()
            return self
        return super(MoneyArray, self).astype(dtype)

    # ------------------------------------------------------------------------
    # Ops
    # ------------------------------------------------------------------------

    def __eq__(self, other):
        # Currently, this does not account for exchange, unlike other comparators
        if not isinstance(other, MoneyArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        result = self.data == other.data
        result[mask] = False
        return result

    def __lt__(self, other):
        if not isinstance(other, MoneyArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        same = (self.data['cu'] == other.data['cu']) | mask
        result = (self.data['va'] < other.data['va'])
        for i, ceq in enumerate(same):
            if not ceq:
                result[i] = money.XMoney(*self.data[i]) < money.XMoney(*self.other[i])

        result[mask] = False
        return result

    def __le__(self, other):
        if not isinstance(other, MoneyArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        same = (self.data['cu'] == other.data['cu']) | mask
        result = (self.data['va'] < other.data['va'])
        for i, ceq in enumerate(same):
            if not ceq:
                result[i] = money.XMoney(*self.data[i]) < money.XMoney(*self.other[i])

        result[mask] = False
        return result

    def __gt__(self, other):
        if not isinstance(other, MoneyArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        same = (self.data['cu'] == other.data['cu']) | mask
        result = (self.data['va'] > other.data['va'])
        for i, ceq in enumerate(same):
            if not ceq:
                result[i] = money.XMoney(*self.data[i]) > money.XMoney(*self.other[i])

        result[mask] = False
        return result

    def __ge__(self, other):
        if not isinstance(other, MoneyArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        same = (self.data['cu'] == other.data['cu']) | mask
        result = (self.data['va'] >= other.data['va'])
        for i, ceq in enumerate(same):
            if not ceq:
                result[i] = money.XMoney(*self.data[i]) < money.XMoney(*self.other[i])

        result[mask] = False
        return result

    def equals(self, other):
        if not isinstance(other, MoneyArray):
            raise TypeError("Cannot compare 'MoneyArray' "
                            "to type '{}'".format(type(other)))
        # TODO: missing
        return (self.data == other.data).all()

    _formatting_values = None
    def _formatter(self, boxed=False):
        def fmt(x):
            if isinstance(x, money.XMoney):
                return str(x)
            elif not x:
                return "NA"
        return fmt

    def _values_for_factorize(self):
        return self.astype(object), (0, '')

    def to_currency(self, money_code, shallow=True, in_place=False):
        if shallow:
            if in_place:
                copy = self
            else:
                copy = self.copy()
            copy.default_money_code = money_code
        else:
            mask = self.isna()
            same = (self.data['cu'] == money_code) | mask
            decimalize = np.vectorize(decimal.Decimal)

            result = self.data
            if not in_place:
                result = result.copy()

            for i, ceq in enumerate(same):
                if not ceq:
                    va = money.XMoney(self.data[i]['va'], self.data[i]['cu']) \
                           .to(money_code).amount
                    result[i] = (va, money_code)

            if in_place:
                self.data = result
            copy = self.__class__(
                result,
                default_money_code=money_code,
                dtype=self.dtype
            )

        return copy

# -----------------------------------------------------------------------------
# Accessor
# -----------------------------------------------------------------------------


@pd.api.extensions.register_series_accessor("money")
class MoneyAccessor:

    isna = DelegatedMethod("isna")

    def __init__(self, obj):
        self._validate(obj)
        self._data = obj.values
        self._index = obj.index
        self._name = obj.name

    @staticmethod
    def _validate(obj):
        if not is_money_type(obj):
            raise AttributeError("Cannot use 'money' accessor on objects of "
                                 "dtype '{}'.".format(obj.dtype))

    def to_currency(self, money_code, shallow=True, in_place=True):
        return delegated_method(
            self._data.to_currency,
            self._index,
            self._name,
            money_code,
            shallow,
            in_place
        )


def is_money_type(obj):
    t = getattr(obj, 'dtype', obj)
    try:
        return isinstance(t, MoneyType) or issubclass(t, MoneyType)
    except Exception:
        return False
