# pylint: disable=protected-access, missing-function-docstring, fixme
"""
Unit tests for parser.
"""
import pytest
from iso4217parse import Currency
import money
from moneypandas import parser, MoneyArray


@pytest.mark.parametrize('values', [
    [u'123 EUR',
     u'234 EUR']
    # TODO: reinstate byte tests
    # [b'\xc0\xa8\x01\x01',
    # b' \x01\r\xb8\x85\xa3\x00\x00\x00\x00\x8a.\x03ps4'],
])
def test_to_money(values):
    result = parser.to_money(values)
    expected = MoneyArray([
        123,
        234
    ], 'EUR')
    assert result.equals(expected)


@pytest.mark.parametrize('val, expected, money_code', [
    (u'123 EUR', money.XMoney(123, 'EUR'), None),
    (123, money.XMoney(123, 'EUR'), 'EUR'),
    (money.XMoney(100, 'GBP'), money.XMoney(100, 'GBP'), None)
])
def test_as_money_object(val, expected, money_code):
    result = parser._as_money_object(val, money_code)
    assert result == (expected.amount, expected.currency)


@pytest.mark.parametrize("val", [
    u"129", -1
])
def test_as_money_object_raises(val):
    with pytest.raises(ValueError):
        parser._as_money_object(val)


def test__currency_symbol():
    """ testing the value returned from _currency_symbol """
    expected = [Currency(
        alpha3='USD',
        code_num=840,
        name='United States dollar',
        symbols=['US$', '$', '＄', '﹩', 'dollar',
                 'dollars', 'Dollar', 'Dollars', 'US＄', 'US﹩'],
        minor=2,
        countries=['AS', 'BB', 'BM', 'BQ', 'EC', 'FM', 'GU', 'HT', 'IO', 'MH',
                   'MP', 'PA', 'PR', 'PW', 'SV', 'TC', 'TL', 'UM', 'US', 'VG', 'VI']
    )]
    test_value = 'USD 4'
    result = parser._currency_symbol(test_value)
    assert result == expected
