#!/bin/sh

pylint dockermirror
PYTHONPATH=. pytest --cov=dockermirror -vv
