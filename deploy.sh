# !/bin/bash


rm -rf dist/*
#sed -i -e 's/DEV=True/DEV=False/g' "manafa/utils/Utils.py"
python -m incremental.update manafa --patch
echo "" > manafa/results/batterystats/__init__.py
echo "" > manafa/results/hunter/__init__.py
echo "" > manafa/results/perfetto/__init__.py
git add manafa/_version.py manafa/utils/Utils.py manafa/results/*/__init__.py
git commit -m "bump _version"
python setup.py sdist
python -m twine upload dist/*