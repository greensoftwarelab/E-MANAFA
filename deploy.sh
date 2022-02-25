# !/bin/bash
sem_ver="patch"
test "$1" == "patch" && sem_ver="patch"
test "$1" == "minor" && sem_ver="minor"
test "$1" == "major" && sem_ver="major"
rm -rf dist/* build/*
python3 -m incremental.update manafa "--${sem_ver}"
echo "" > manafa/results/batterystats/__init__.py
echo "" > manafa/results/hunter/__init__.py
echo "" > manafa/results/perfetto/__init__.py
echo "" > manafa/results/consumptions/__init__.py
git add manafa/_version.py manafa/utils/Utils.py manafa/results/*/__init__.py
git commit -m "bump _version"
python3 setup.py clean
python3 setup.py sdist
python3 -m twine upload dist/*
git push origin main