#!/usr/bin/env bash
set -e
echo "Building moneypandas"

conda build -c defaults -c conda-forge conda-recipes/moneypandas --python=${PYTHON}
