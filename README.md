# Moneypandas

Moneypandas is a prototype fork of Cyberpandas for currency, using the `money` library. Even this README is shamelessly purloigned, with thanks to Tom Augspurger and the ContinuumIO team.

This package provides support for storing currency data inside a pandas DataFrame using pandas' [Extension Array Interface](http://pandas-docs.github.io/pandas-docs-travis/extending.html#extension-types)

```python
In [1]: from moneypandas import MoneyArray

In [2]: import pandas as pd

In [3]: df = pd.DataFrame({"money": MoneyArray(['1284 EUR', '121 EUR', '€14'])})

In [4]: df
Out[4]:
          money
0  EUR 1,284.00
1    EUR 121.00
2     EUR 14.00
```

For more examples, including summing and converting mixed-currency columns, see the `examples` folder.

(note: not yet tested with Conda, only setuptools/pipenv)

To efficiently perform operations, aggregation is done per currency first, and then XMoney used to do necessary operations on the output aggregates.

Currency conversion of a Series only uses XMoney and conversion where currencies mismatch, so converting a column mostly of BBBs, with a few AAAs, should scale according to the number of AAAs.

## TODO

* implement more reduce functions
* testing for arithmetic
