#!/usr/bin/env bash

INIT_WD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";

cd "$INIT_WD"/docsrc || exit

make clean
make github

sphinx-build . ./_build
