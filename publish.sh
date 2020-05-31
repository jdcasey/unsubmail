#!/bin/bash

source .venv/bin/activate || exit 1

pip install --upgrade pip twine bumpversion || exit 2

python setup.py sdist bdist_wheel || exit 3

echo "This is what we're publishing:"
tar tzf dist/unsubmail-*.tar.gz

twine check dist/* || exit 4

twine upload --repository-url https://test.pypi.org/legacy/ dist/* || exit 5

read -n 1 -p "Please go check https://test.pypi.org/ for the updated package. Then, hit <ENTER> to continue." go_on

twine upload dist/* || exit 6
