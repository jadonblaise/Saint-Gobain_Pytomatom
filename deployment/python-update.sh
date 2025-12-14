# ! run all lines manually.. this is not a script

pyenv update
pyenv install <new-version>
pyenv rehash
# ! edit pythonversion in /etc/profile.d/pythonversion.sh

su - $appuser

poetry config virtualenvs.in-project true
$POETRY_HOME/bin/poetry config cache-dir $POETRY_HOME/.cache
poetry install
