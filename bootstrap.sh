#!/bin/bash

set -ex

PYTHON_VERSION=3.10.9
VIRTUALENV_NAME=aws-log-parser-${PYTHON_VERSION}

cd $PYENV_ROOT
git pull
cd -

echo "${VIRTUALENV_NAME}" > .python-version

eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
pyenv install -s ${PYTHON_VERSION}
if [ ! -e "${PYENV_ROOT}/versions/${VIRTUALENV_NAME}" ]; then
    pyenv virtualenv ${PYTHON_VERSION} ${VIRTUALENV_NAME}
fi
pyenv activate ${VIRTUALENV_NAME}
pip install --upgrade pip
pip install -e .
pip install -r requirements/all.txt
pre-commit install
