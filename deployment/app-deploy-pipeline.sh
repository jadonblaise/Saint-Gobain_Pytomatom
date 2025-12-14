#!/bin/bash

# Automated deployment pipeline for the app CI/CD.

# Read POETRY_HOME
export POETRY_HOME=$(grep "^POETRY_HOME=" /etc/profile.d/poetry.sh | cut -d= -f2)
# Read app variables as key value pairs
export $(cat /etc/profile.d/app.sh | xargs)
export DOPPLER_TOKEN=$(cat "/root/.doppler/$appname-token")
DEPLOYMENT_TOKEN=$(doppler secrets download --format=json --no-file --config=production | jq -r '.DEPLOYMENT_TOKEN')
GITHUB_REPO_URL=https://machine-sgdigital:$DEPLOYMENT_TOKEN@github.com/061-Digital-IT-Germany-Austria/pytomatom

# DOPPLER_TOKEN=$DOPPLER_TOKEN GITHUB_REPO_URL=$GITHUB_REPO_URL POETRY_HOME=$POETRY_HOME appuser=$appuser appversion=$appversion appname=$appname appdir=$appdir $appdir/src/deployment/app-deploy.sh

POETRY_HOME=$POETRY_HOME \
DOPPLER_TOKEN=$DOPPLER_TOKEN \
GITHUB_REPO_URL=$GITHUB_REPO_URL \
appuser=$appuser \
appname=$appname \
appdir=$appdir \
    $appdir/src/deployment/app-deploy.sh && chmod +x $appdir/src/deployment/app-deploy.sh

chmod +x $appdir/src/deployment/app-deploy.sh

/bin/cp --force $appdir/src/deployment/app-deploy-pipeline.sh /opt/bin/app-deploy-pipeline.sh
chmod +x /opt/bin/app-deploy-pipeline.sh

echo "Finished app-deploy-pipeline.sh"
