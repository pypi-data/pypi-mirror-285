#!/bin/sh
set -e  # Configure shell so that if one command fails, it exits
pip install -U pip
pip install -r /opt/app/requirements/test.txt
coverage erase
coverage run -m pytest
python -m flake8 --max-line-length=88 --exclude .git,__pycache__,.eggs,build
coverage report
coverage html
coverage-badge

