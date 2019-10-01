from moneypandas import MoneyArray
from money import xrates
import decimal
import pandas as pd


xrates.install('money.exchange.SimpleBackend')
xrates.base = 'USD'
xrates.setrate('EUR', decimal.Decimal('0.9'))
xrates.setrate('GBP', decimal.Decimal('0.8'))

df_gbp = pd.DataFrame({"money_gbp": MoneyArray(['£100'], 'USD')})
df_eur = pd.DataFrame({"money_eur": MoneyArray(['EUR 300'], 'USD')})

# to find the difference between 2 currencies, will need to specify the currency to output the difference in

# attempting to subtract two data frames. it's currently outputting the difference in EUR so it needs to be converted to USD
difference_in_usd = df_eur['money_eur'].sub(df_gbp['money_gbp'])
print(difference_in_usd)
