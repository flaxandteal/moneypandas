"""Custom IP address dtype / block for pandas"""

from .money_array import (
    MoneyType,
    MoneyArray,
    MoneyAccessor,
)
from .parser import to_money

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

del get_distribution
del DistributionNotFound


__all__ = [
    '__version__',
    'MoneyAccessor',
    'MoneyArray',
    'MoneyType',
    'to_money',
]
