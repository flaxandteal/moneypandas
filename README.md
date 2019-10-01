# Moneypandas

Moneypandas is a prototype fork of Cyberpandas for currency, using the `money` library. Even this README is shamelessly purloigned, with thanks to Tom Augspurger and the ContinuumIO team.

This package provides support for storing currency data inside a pandas DataFrame using pandas' [Extension Array Interface](http://pandas-docs.github.io/pandas-docs-travis/extending.html#extension-types)


## Set Up Dev Environment

Run `pipenv shell` or another Python3 virtual envirnonment.

Run `python3 setup.py develop`

The env should be set up. Run `python3 examples/three_currency.py` to check.

## Contributing (For new open source contributers!)

Clone this repo using `SSH` or `HTTPS`

For any changes, do `git checkout -b [feature/bug][description-of-issue]` to create a new branch.

Once your changes are made, `git add [file-name]`. Add each file individually.

Run `git status` to make sure all the files you want are added to this commit.

Do `git commit -m "A message describing what changes you made, and why, possible bugs, and what you want to do"`. This will make it easier to refer back to in future.

Run `git push -u origin [branch-name]`. If there have been no issues then a pull request should be open. Follow the link that was returned in the console to complete the PR.


___

## Example

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
