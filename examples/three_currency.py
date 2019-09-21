from moneypandas import MoneyArray
from money import xrates
import decimal
import pandas as pd


xrates.install('money.exchange.SimpleBackend')
xrates.base = 'USD'
xrates.setrate('EUR', decimal.Decimal('0.9'))
xrates.setrate('GBP', decimal.Decimal('0.8'))

df = pd.DataFrame({"money": MoneyArray(['1284 EUR', '121 EUR', '€14', '£12'], 'USD')})
total = df['money'].sum()
print("Total: ", total)
print("Total (EUR): ", total.to('EUR'))

df['money'] = df['money'].money.to_currency('EUR')
mean = df['money'].mean()
print("Mean: ", mean)

df['money'].money.to_currency('GBP', shallow=False, in_place=True)
print('All converted to GBP', df)
