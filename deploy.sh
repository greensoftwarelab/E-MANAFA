# !/bin/bash


rm -rf dist/*
python -m incremental.update manafa --patch
git add manafa/_version.py
git commit -m "bump _version"
python setup.py sdist
python -m twine upload dist/*