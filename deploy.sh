# !/bin/bash

rm -rf dist/*
python -m incremental.update manafa --patch
python setup.py sdist
python -m twine upload dist/*