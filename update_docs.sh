#!/usr/bin/env bash
sphinx-apidoc -f -e -o $PWD/docs/ src/friendlyshell
mkdir docs/_static
pushd docs
make html
popd
open docs/_build/html/index.html