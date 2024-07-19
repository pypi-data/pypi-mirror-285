#!/usr/bin/env bash
set -e

maturin develop
time MYPYPATH=. python -m mypy stringanalysis
time python -m pytest -vv

# For a debug build, use these commands instead of the ones above:
#
# time RUSTFLAGS="-C link-args=-L$(find "$(dirname "$(ls -l $(which python) | sed 's|.*-> ||')")/.." -name 'libpython*so') -lpython3.7dm" maturin develop
# gdb -return-child-result -batch -ex r -ex bt --args python -m pytest
