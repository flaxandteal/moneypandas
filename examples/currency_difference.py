from money import XMoney
from money import xrates
import decimal
import pandas as pd

# install abstract base class
xrates.install('money.exchange.SimpleBackend')
#set US Dollar as the currency the others will be converted to
xrates.base = 'USD'
# set the exchange rate for EUR to USD
xrates.setrate('EUR', decimal.Decimal('0.9'))
# set the exchange rate for GBP to USD
xrates.setrate('GBP', decimal.Decimal('0.8'))

# data frame - uses Pandas' Extension Array Interface
df = pd.DataFrame({"money": MoneyArray(['GBP 100', 'EUR 300'], 'USD')})
print("The table with the currencies:\n", df)
# the data frame table is accessed via the row, ie 0 is row 1 & 1 is row 2.
# the subtraction method needs accessed through XMoney, a money subclass. Then it's converted to USD
difference = (df['money'][0].__sub__(df['money'][1])).to('USD')
print("\nDifference between GBP 100 & EUR 300, in USD:\n", difference)


