#!/bin/bash

# will run as the $appname user

if [ -z "$POETRY_HOME" ]; then echo "POETRY_HOME is not set"; exit 1; fi
if [ -z "$appdir" ]; then echo "appdir is not set"; exit 1; fi

pushd $appdir/src

# Ensure newest version of pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$appdir/src/.venv/bin/python get-pip.py --force-reinstall
rm get-pip.py
# $appdir/src/.venv/bin/python -m pip install --upgrade pip
# Install the app's dependencies
$POETRY_HOME/bin/poetry config virtualenvs.in-project true
$POETRY_HOME/bin/poetry config cache-dir $appdir/.cache
$POETRY_HOME/bin/poetry install --no-root

# To manually activate the venv.. switch to the appuser
# source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.production $appdir/src/.venv/bin/python commands.py setup --production --no-panic
DJANGO_SETTINGS_MODULE=config.settings.production $appdir/src/.venv/bin/python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.production $appdir/src/.venv/bin/python manage.py createcachetable

# Frontend installation
pushd $appdir/src/frontend
rm --recursive --force node_modules/ && yarn install && yarn build
popd

DJANGO_SETTINGS_MODULE=config.settings.production $appdir/src/.venv/bin/python manage.py collectstatic --noinput --clear --verbosity 0

popd
