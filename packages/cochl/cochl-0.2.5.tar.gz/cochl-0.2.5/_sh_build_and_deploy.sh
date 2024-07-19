#!/bin/sh

sudo apt install python3.8
sudo apt install python3.8-venv

python3.8 --version

python3.8 -m pip install --upgrade pip

python3.8 -m pip install --upgrade build

rm -rf .github
rm -rf dist
mkdir dist
rm -rf samples
rm -rf tests
rm -rf .gitignore
rm -rf HOME_dot_pypirc
rm -rf README_hglim.md

python3.8 -m build

git reset --hard

python3.8 -m pip install --upgrade twine
# python3.8 -m twine upload --repository testpypi dist/*
python3.8 -m twine upload dist/* --verbose

# python3.8 -c 'import cochl.sense; print(cochl.sense.APIConfig())'
