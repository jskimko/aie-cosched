#!/bin/sh
# The paper's data figures and generated table rows into paper/fig (figs/make_figs.py).
set -e
cd "$(dirname "$0")/.."
FIGS_OUT=paper/fig .venv/bin/python figs/make_figs.py
