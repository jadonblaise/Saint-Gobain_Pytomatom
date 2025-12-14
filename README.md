# pytomatom

Automation for the "Saint-Gobain Glaswerk" in Porz.  
    - Order Management  
    - Integration of data lake access
    - Planned: Demand Forecast  

Realised as a django project (planned: with a postgresql database).  
Python's project dependencies are managed by [poetry](https://python-poetry.org/).  
See [pyproject.toml](pyproject.toml) for the list of dependencies.


## Production server

TLDR: redeploy (see below)

```bash
ssh pytomatom
sudo /opt/bin/app-deploy-pipeline.sh
# enter credentials
```

TLDR: datalake access

```bash
email: DL-Dti-datalake-team@saint-gobain.com
password: secret
```


As preparation for your ssh connection. Generate a key
```powershell
ssh-keygen -t rsa -b 4096 -C "Pytomatom production KEY." -f $env:USERPROFILE\.ssh\SSH_KEY_PYTOMATOM_PRODUCTION_id_rsa
# manully add that key to authorized_keys on the server
# (copy the local content of `$env:USERPROFILE\.ssh\SSH_KEY_PYTOMATOM_PRODUCTION_id_rsa.pub` to the server
# `/home/sgadmin/.ssh/authorized_keys`)
```

## sharepoint

Entra admin interface:
https://entra.microsoft.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/0247c286-a670-457d-9b4a-802c731bcedb


https://entra.microsoft.com/#view/Microsoft_AAD_IAM/ManagedAppMenuBlade/~/Overview/objectId/49772399-97dc-4ad3-bfc1-a832c6ae7501/appId/0247c286-a670-457d-9b4a-802c731bcedb

Credentials: `.secrets/sharepoint.password.json`


## Setup & developing

- [How-to-clone-and-ssh](./documentation/for-developers/how-to-clone-and-ssh.md).
- [How-to-develop basics](./documentation/for-developers/how-to-develop.md).
- [jupyter notebooks for fast debugging](./documentation/for-developers/notebooks.md).


### Install dependencies

    # either install all requirements
    python -m pip wheel --use-pep517 "pure-sasl (==0.6.2)"
    poetry install

    # cherry pick the ones you need
    poetry install --with authentication,restframework,vite --without postgres,paragons

    # or install only the root dependencies (updating the lock file)
    poetry install --only-root --sync


### Setup the project

    # poetry run python commands.py doppler (not finished - for the first time do it manually on console in root project's path - find commands in method's comments)

    poetry run python commands.py setup

    # you need Docker (WSL on Windows as well),
    # Docker-Compose,
    # PostgreSQL,
    # Redes
    # find information about further bellow
    poetry run python manage.py migrate
    poetry run python manage.py createcachetable


### Deployment

See the [documentation on deployments](./documentation/for-devops/deployment.md) for details.

```bash
# have the server key & the admin password ready
ssh pytomatom
sudo /opt/bin/app-deploy-pipeline.sh
```

The sshconfig.

```bash
Host pytomatom
    HostName ODESVLPOR001AP
    User sgadmin
    Port 22
    IdentityFile ~/.ssh/SSH_KEY_PYTOMATOM_PRODUCTION_id_rsa
```

Shell for appuser (python and management commands are directly available).

```bash
sudo su - app
```

### Pre-Commit hooks

[Pre-commit hooks](https://github.com/pre-commit/pre-commit-hooks) are defined
in `.pre-commit-config.yaml`. Adding them to the project will ensure that the
code is formatted and linted before committing. Repeat the installation
everytime you re-create the venv  

    poetry run pre-commit install

TODO: reactivate pyupgrade after the support for typing.Optional is added in 1.0 of typer


### Tests

Run [pytest](https://docs.pytest.org/).

    poetry run pytest


### Linter

Lint with [ruff](https://github.com/charliermarsh/ruff) and [flake8](https://github.com/PyCQA/flake8).

    poetry run ruff check .
    poetry run flake8


### Formatter

Autoformatting is enforced with industry-standard [black](https://github.com/psf/black).

    poetry run black --check .


### Type checker

Static type checking can be checked with [mypy](https://mypy-lang.org/).

    poetry run mypy --config-file pyproject.toml .

To let the mypy daemon (dmypy) work with your ide, install the following packages in the env, that is used by your ide (you can validate these packes with your pre-commit-config.yml as well):

    pip install mypy django-stubs[compatible-mypy] djangorestframework-stubs[compatible-mypy]

    pip install Django django-stubs-ext environs django-cors-headers django-csp django-permissions-policy django_celery_results msgspec rich gitpython tomlkit python-jose djangorestframework django-crispy-forms crispy-tailwind django-extensions django-rich django-hatchway django-readers django-widget-tweaks django-vite django-debug-toolbar psycopg psycopg-binary jinja2 celery django-celery-beat django-celery-results redis django-redis djhtml typer coverage pytest pytest-django pytest-rich pytest-cov pytest-vcr pytest-instafail hypothesis faker freezegun djhtml humanize pendulum dill passlib httpx textual doppler-env msal


### celery

- [celery](https://docs.celeryq.dev/) & [celery-beat](https://github.com/celery/django-celery-beat)

(develop) start the beat, who can't live without the worker

    $env:DJANGO_SETTINGS_MODULE="config.settings.develop"; celery --app config.celeryapp beat --loglevel=INFO  --scheduler django_celery_beat.schedulers:DatabaseScheduler

(develop) start the worker

    $env:DJANGO_SETTINGS_MODULE="config.settings.develop"; celery --app config.celeryapp worker --loglevel=INFO --queues celery,pytomatom --pool solo

Ocassionally it's good to purge all (old) celery tasks

    # correctly set the DJANGO_SETTINGS_MODULE environment variable in
    # powershell
    $env:DJANGO_SETTINGS_MODULE="config.settings.develop"
    # or posix
    DJANGO_SETTINGS_MODULE=config.settings.develop

    # Then purge all tasks from queues celery and pytomatom
    $env:DJANGO_SETTINGS_MODULE="config.settings.develop"; celery --app config.celeryapp purge --queues pytomatom,celery


```python manage.py shell
# or
from config.celeryapp import app
app.control.purge()
```

```python manage.py shell
# FIXME: Debugging tasks (has not too many results yet unfortunately... (all None??!))
from django_celery_results.models import TaskResult
TaskResult(task_id)
```

```bash
# clear redis cache..
redis-cli -h localhost -p 6379 -a <PASSWORD> -n 1 FLUSHALL
```

```python manage.py shell
# manual setup for task debugging
from config.celeryapp import app
from celery.app.control import Control
from celery.result import AsyncResult

app.config_from_object("django.conf:settings", namespace="CELERY")

control = Control(app)
inspected = control.inspect()

scheduled = inspected.scheduled()
active = inspected.active()
reserved = inspected.reserved()
queues = inspected.active_queues()
registered = inspected.registered()

task_id = "?" # from logs?

AsyncResult(task_id).revoke(terminate=True)
```


## Preinstalled third party packages

### root (default)
- [msgspec](https://jcristharif.com/msgspec/)

### develop
- [jupyter](https://jupyter.org/)
- [typer](https://typer.tiangolo.com/)
- [ruff](https://github.com/charliermarsh/ruff)
- [pytest](https://docs.pytest.org/)
- [faker](https://faker.readthedocs.io/en/master/)

### django
- [django-readers](https://www.django-readers.org/)
- [django-hatchway](https://github.com/andrewgodwin/django-hatchway)
- [django-cripsy-forms](https://django-crispy-forms.readthedocs.io/)

### paragons
- [rich](https://github.com/Textualize/rich)
- [humanize](https://python-humanize.readthedocs.io/)
- [pendulum](https://pendulum.eustace.io/)
- [dill](https://github.com/uqfoundation/dill)
- [passlib](https://passlib.readthedocs.io/en/stable/)
- [httpx](https://www.python-httpx.org/)

### restframework
- [djangorestframework](https://www.django-rest-framework.org/)

### authentication
- [jose](https://github.com/mpdavis/python-jose)

### vite
- [django-vite](https://github.com/MrBin99/django-vite)

and many more..
