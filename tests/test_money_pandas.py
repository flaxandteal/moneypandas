"""Tests involving pandas, not just the new array.
"""
import money

import pytest
import numpy as np
from hypothesis.strategies import integers, lists
from hypothesis import given
import pandas as pd
from pandas.core.internals import ExtensionBlock
import pandas.util.testing as tm

import moneypandas as mpd


# ----------------------------------------------------------------------------
# Block Methods
# ----------------------------------------------------------------------------


def test_concatenate_blocks():
    v1 = mpd.MoneyArray([1, 2, 3], 'GBP')
    s = pd.Series(v1, index=pd.RangeIndex(3), fastpath=True)
    result = pd.concat([s, s], ignore_index=True)
    expected = pd.Series(mpd.MoneyArray([1, 2, 3, 1, 2, 3], 'GBP'))
    tm.assert_series_equal(result, expected)


# ----------------------------------------------------------------------------
# Public Constructors
# ----------------------------------------------------------------------------


def test_series_constructor():
    v = mpd.MoneyArray([1, 2, 3], 'USD')
    result = pd.Series(v)
    assert result.dtype == v.dtype
    assert isinstance(result._data.blocks[0], ExtensionBlock)


def test_dataframe_constructor():
    v = mpd.MoneyArray([1, 2, 3], 'USD')
    df = pd.DataFrame({"A": v})
    assert isinstance(df.dtypes['A'], mpd.MoneyType)
    assert df.shape == (3, 1)
    str(df)


def test_dataframe_from_series_no_dict():
    s = pd.Series(mpd.MoneyArray([1, 2, 3], 'INR'))
    result = pd.DataFrame(s)
    expected = pd.DataFrame({0: s})
    tm.assert_frame_equal(result, expected)

    s = pd.Series(mpd.MoneyArray([1, 2, 3], 'INR'), name='A')
    result = pd.DataFrame(s)
    expected = pd.DataFrame({'A': s})
    tm.assert_frame_equal(result, expected)


def test_dataframe_from_series():
    s = pd.Series(mpd.MoneyArray([0, 1, 2], 'EUR'))
    c = pd.Series(pd.Categorical(['a', 'b']))
    result = pd.DataFrame({"A": s, 'B': c})
    assert isinstance(result.dtypes['A'], mpd.MoneyType)


def test_getitem_scalar():
    ser = pd.Series(mpd.MoneyArray([None, 1, 2], 'USD'))
    result = ser[1]
    assert result == money.XMoney(1, 'USD')


def test_getitem_slice():
    ser = pd.Series(mpd.MoneyArray([0, 1, 2], 'EUR'))
    result = ser[1:]
    expected = pd.Series(mpd.MoneyArray([1, 2], 'EUR'), index=range(1, 3))
    tm.assert_series_equal(result, expected)


def test_setitem_scalar():
    ser = pd.Series(mpd.MoneyArray([0, 1, 2], 'EUR'))
    ser[1] = money.XMoney(10, 'EUR')
    expected = pd.Series(mpd.MoneyArray([0, 10, 2], 'EUR'))
    tm.assert_series_equal(ser, expected)


# --------------
# Public Methods
# --------------


@given(lists(integers(min_value=1, max_value=2**128 - 1)))
def test_argsort(ints):
    pass
    # result = pd.Series(mpd.MoneyArray(ints)).argsort()
    # expected = pd.Series(ints).argsort()
    # tm.assert_series_equal(result.mpd.to_decimals('GBP'), expected)


# --------
# Accessor
# --------

#def test_non_money_raises():
#    s = pd.Series([1, 2])
#
#    with pytest.raises(AttributeError) as m:
#        s.money.is_currency('EUR')
#
#    assert m.match("Cannot use 'money' accessor on objects of dtype 'int.*")


#def test_accessor_works():
#    s = pd.Series(mpd.MoneyArray([0, 1, 2, 3], 'USD'))
#    s.money.is_currency('USD')


#def test_accessor_frame():
#    s = pd.DataFrame({"A": mpd.MoneyArray([0, 1, 2, 3], 'EUR')})
#    s['A'].money.is_currency('USD')


# ---------
# Factorize
# ---------


@pytest.mark.xfail(reason="TODO")
def test_factorize():
    arr = mpd.MoneyArray([1, 1, 10, 10], 'JPY')
    labels, uniques = pd.factorize(arr)

    expected_labels = np.array([0, 0, 1, 1])
    tm.assert_numpy_array_equal(labels, expected_labels)

    expected_uniques = mpd.MoneyArray([1, 10], 'JPY')
    assert uniques.equals(expected_uniques)


@pytest.mark.xfail(reason="TODO")
def test_groupby_make_grouper():
    df = pd.DataFrame({"A": [1, 1, 2, 2],
                       "B": mpd.MoneyArray([1, 1, 2, 2], 'EUR')})
    gr = df.groupby("B")
    result = gr.grouper.groupings[0].grouper
    assert result.equals(df.B.values)


@pytest.mark.xfail(reason="TODO")
def test_groupby_make_grouper_groupings():
    df = pd.DataFrame({"A": [1, 1, 2, 2],
                       "B": mpd.MoneyArray([1, 1, 2, 2], 'EUR')})
    p1 = df.groupby("A").grouper.groupings[0]
    p2 = df.groupby("B").grouper.groupings[0]

    result = {int(k): v for k, v in p2.groups.items()}
    assert result.keys() == p1.groups.keys()
    for k in result.keys():
        assert result[k].equals(p1.groups[k])
