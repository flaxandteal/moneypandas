import pytest
import pandas.util.testing as tm
import pandas as pd
from pandas.tests.extension import base
from pandas.tests.extension.conftest import *
import numpy as np

import moneypandas as mpd


@pytest.fixture
def dtype():
    return mpd.MoneyType()


@pytest.fixture
def data():
    ma = mpd.MoneyArray(list(range(1, 101)), 'USD')
    return ma


@pytest.fixture
def data_missing():
    return mpd.MoneyArray([np.nan, 1], 'USD')


@pytest.fixture(params=['data', 'data_missing'])
def all_data(request, data, data_missing):
    """Parametrized fixture giving 'data' and 'data_missing'"""
    if request.param == 'data':
        return data
    elif request.param == 'data_missing':
        return data_missing


@pytest.fixture
def data_for_sorting():
    return mpd.MoneyArray([10, 123, 1], default_money_code='GBP')


@pytest.fixture
def data_missing_for_sorting():
    return mpd.MoneyArray([2, None, 1], default_money_code='GBP')


@pytest.fixture
def data_for_grouping():
    b = 1
    a = 233
    c = 242
    return mpd.MoneyArray([
        b, b, np.nan, None, a, a, b, c
    ], 'USD')


@pytest.fixture
def data_repeated(data):
    def gen(count):
        for _ in range(count):
            yield data
    return gen


@pytest.fixture
def na_cmp():
    """Binary operator for comparing NA values.

    Should return a function of two arguments that returns
    True if both arguments are (scalar) NA for your type.

    By default, uses ``operator.or``
    """
    return lambda x, y: pd.isna(x) and pd.isna(y)


@pytest.fixture
def na_value():
    return mpd.MoneyType.na_value


class TestDtype(base.BaseDtypeTests):
    pass


class TestInterface(base.BaseInterfaceTests):
    pass


class TestConstructors(base.BaseConstructorsTests):
    pass


class TestReshaping(base.BaseReshapingTests):
    @pytest.mark.skip("We consider 0 to be NA.")
    def test_stack(self):
        pass

    @pytest.mark.skip("We consider 0 to be NA.")
    def test_unstack(self):
        pass


class TestGetitem(base.BaseGetitemTests):
    pass


class TestMissing(base.BaseMissingTests):
    pass


class TestMethods(base.BaseMethodsTests):
    @pytest.mark.parametrize('dropna', [True, False])
    @pytest.mark.xfail(reason='upstream')
    def test_value_counts(data, dropna):
        pass

    @pytest.mark.skip(reason='0 for NA')
    def test_combine_le(self, data_repeated):
        super().test_combine_le(data_repeated)

    @pytest.mark.skip(reason='No __add__')
    def test_combine_add(self, data_repeated):
        super().test_combine_add(data_repeated)

    def test_argsort_missing_array(self, data_missing_for_sorting):
        result = data_missing_for_sorting.argsort()
        expected = np.array([1, 2, 0], dtype=np.dtype("int"))
        # we don't care whether it's int32 or int64
        result = result.astype("int64", casting="safe")
        expected = expected.astype("int64", casting="safe")
        tm.assert_numpy_array_equal(result, expected)
