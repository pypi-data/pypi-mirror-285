#!/usr/bin/env bash

set -exu -o pipefail

pdm install
pdm run ruff check src
pdm run mypy src --strict
pdm run pytest tests --durations=5 --cov=. --cov-fail-under=85 --cov-report term
