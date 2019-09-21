import money
import decimal
import operator

import pytest
import six
from hypothesis.strategies import integers, lists, tuples
from hypothesis import given, example

import numpy as np
import numpy.testing as npt
import pandas as pd
import moneypandas as mpd
import pandas.util.testing as tm


def test_make_container():
    values = mpd.MoneyArray([1, 2, 3], 'GBP')
    npt.assert_array_equal(
        values.data,
        np.array([(1, 'GBP'),
                  (2, 'GBP'),
                  (3, 'GBP')], dtype=values.dtype._record_type)
    )


def test_repr_works():
    values = mpd.MoneyArray([0, 1, 2, 3], 'GBP')
    result = repr(values)
    expected = ("<MoneyArray[GBP]>\n[GBP 0.00, GBP 1.00, GBP 2.00, GBP 3.00]\nLength: 4, dtype: money")
    assert result == expected


def test_isna():
    v = mpd.MoneyArray([None, 2], 'GBP')
    r1 = v.isna()
    r2 = pd.isna(v)
    expected = np.array([True, False])

    np.testing.assert_array_equal(r1, expected)
    np.testing.assert_array_equal(r2, expected)


def test_array():
    v = mpd.MoneyArray([1, 2, 3], 'GBP')
    result = np.array(v)
    expected = np.array([
        money.XMoney(1, 'GBP'),
        money.XMoney(2, 'GBP'),
        money.XMoney(3, 'GBP'),
    ])
    tm.assert_numpy_array_equal(result, expected)


def test_tolist():
    v = mpd.MoneyArray([1, 2, 3], 'USD')
    result = v.tolist()
    expected = [(1, 'USD'), (2, 'USD'), (3, 'USD')]
    assert result == expected


def test_to_pymoney():
    v = mpd.MoneyArray([1, 2, 3], 'USD')
    result = v.to_pymoney()
    expected = [
        money.XMoney(1, 'USD'),
        money.XMoney(2, 'USD'),
        money.XMoney(3, 'USD'),
    ]
    assert result == expected



def test_equality():
    v1 = mpd.to_money([
        u'123 EUR',
        u'345 GBP',
    ])
    assert np.all(v1 == v1)
    assert v1.equals(v1)

    v2 = mpd.to_money([
        u'124 EUR',
        u'345 GBP',
    ])
    result = v1 == v2
    expected = np.array([False, True])
    tm.assert_numpy_array_equal(result, expected)

    result = bool(v1.equals(v2))
    assert result is False

    with pytest.raises(TypeError):
        v1.equals("a")


@pytest.mark.parametrize('op', [
    operator.lt,
    operator.le,
    operator.ge,
    operator.gt,
])
@pytest.mark.skipif(six.PY2, reason="Flexible comparisons")
def test_comparison_raises(op):
    arr = mpd.MoneyArray([0, 1, 2], 'JPY')
    with pytest.raises(TypeError):
        op(arr, 'a')

    with pytest.raises(TypeError):
        op('a', arr)


@given(
    tuples(
        lists(integers(min_value=0, max_value=99999)),
        lists(integers(min_value=0, max_value=99999))
    ).filter(lambda x: len(x[0]) == len(x[1]))
)
@example((1, 1))
@example((0, 0))
@example((0, 1))
@example((1, 0))
@example((1, 2))
@example((2, 1))
@pytest.mark.skip(reason="Flaky")
def test_ops(tup):
    a, b = tup
    v1 = mpd.MoneyArray(a, 'GBP')
    v2 = mpd.MoneyArray(b, 'GBP')

    r1 = v1 <= v2
    r2 = v2 >= v1
    tm.assert_numpy_array_equal(r1, r2)


@pytest.mark.xfail(reason='upstream')
def test_value_counts():
    x = mpd.MoneyArray([0, 0, 1], 'USD')
    result = x.value_counts()
    assert len(result)


def test_iter_works():
    x = mpd.MoneyArray([0, 1, 2], 'GBP')
    result = list(x)
    expected = [
        money.XMoney(0, 'GBP'),
        money.XMoney(1, 'GBP'),
        money.XMoney(2, 'GBP'),
    ]
    assert result == expected


def test_todecimal():
    values = [0, 1, 2]
    arr = mpd.MoneyArray(values, 'EUR')
    result = arr.to_decimals()
    assert all([r == decimal.Decimal(v) for r, v in zip(result, values)])


def test_getitem_scalar():
    ser = mpd.MoneyArray([0, 1, 2], 'USD')
    result = ser[1]
    assert result == money.XMoney(1, 'USD')


def test_getitem_slice():
    ser = mpd.MoneyArray([0, 1, 2], 'USD')
    result = ser[1:]
    expected = mpd.MoneyArray([1, 2], 'USD')
    assert result.equals(expected)


@pytest.mark.parametrize('value', [
    u'123 USD',
    123,
    money.XMoney(123, 'USD'),
])
def test_setitem_scalar(value):
    ser = mpd.MoneyArray([0, 1, 2], 'USD')
    ser[1] = value
    expected = mpd.MoneyArray([0, 123, 2], 'USD')
    assert ser.equals(expected)


def test_setitem_array():
    ser = mpd.MoneyArray([0, 1, 2], 'USD')
    ser[[1, 2]] = ['10 USD', '20 USD']
    expected = mpd.MoneyArray([0, 10, 20], 'USD')
    assert ser.equals(expected)


def test_bytes_roundtrip():
    arr = mpd.MoneyArray([1, 2, 3], 'USD')
    bytestring = arr.to_bytes()
    assert isinstance(bytestring, bytes)

    result = mpd.MoneyArray.from_bytes(bytestring)
    assert result.equals(arr)


def test_unique():
    arr = mpd.MoneyArray([3, 3, 1, 2, 3], 'USD')
    result = arr.unique()
    assert isinstance(result, mpd.MoneyArray)

    result = result.astype(object)
    expected = pd.unique(arr.astype(object))
    tm.assert_numpy_array_equal(result, expected)


def test_factorize():
    arr = mpd.MoneyArray([3, 3, 1, 2, 3], 'USD')
    labels, uniques = arr.factorize()
    expected_labels, expected_uniques = pd.factorize(arr.astype(object))

    assert isinstance(uniques, mpd.MoneyArray)

    uniques = uniques.astype(object)
    tm.assert_numpy_array_equal(labels, expected_labels)
    tm.assert_numpy_array_equal(uniques, expected_uniques)


@pytest.mark.parametrize('values', [
    [0, 1, 2],
])
def test_from_ndarray(values):
    result = mpd.MoneyArray(np.asarray(values), 'USD')
    expected = mpd.MoneyArray(values, 'USD')
    assert result.equals(expected)
