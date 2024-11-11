#!/usr/bin/env bash

set -e
set -x

mypy app             # type check
ruff check app          # linter
ruff format app --check # formatter
