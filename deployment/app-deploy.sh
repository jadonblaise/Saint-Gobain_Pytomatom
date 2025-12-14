# This script will redeploy the app.
# If you change credentials for internal services or bigger parts of infrastructure that are not part of the django app
# (like: postgres password, redis password, etc) you should read the rhel.sh and fix it yourself.

# ! run this script as root
# sudo su
pushd $appdir/src

# Pause services, but don't fail if they are not yet setup.
systemctl stop nginx || true
systemctl stop celerybeat || true
systemctl stop celeryworker || true
systemctl stop $appname || true

# Clone the repo, if directory is empty
# Prevent git clone containting the token command being leaked in bash history
export HISTIGNORE='git clone*'
[ -z "$(ls -A $appdir/src)" ] && git clone $GITHUB_REPO_URL $appdir/src || echo "Directory $appdir/src is not empty. I'll skip cloning."


# FIXME: what is the correct git pull here? And when to pull from which branch?
git fetch --all --prune --quiet
# FIXME: when CI/CD and branching is integrated
# git checkout production
git reset --hard
git clean --force --quiet
git pull

# load the envs from doppler - also to have the info on databases etc
doppler --no-check-version configure set config=production
doppler --no-check-version secrets download --format=json --no-file --config=production | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' | awk -F'=' '{print $n}' > $appdir/src/envs/production.env
# add all frontend environment variables (starting with 'VITE_') to the frontend .env.production file
doppler --no-check-version secrets download --format=json --no-file --config=production | jq -r 'to_entries | map(select(.key | startswith("VITE_"))) | .[] | "\(.key)=\(.value)"' > $appdir/src/frontend/.env.production
echo $(doppler --no-check-version secrets download --format=json --no-file --config=production | jq -r '.CERTIFICATE_PASSWORD') > $appdir/certificates/certificate.password
# TBD: certificate must be readable (executable as well?) for nginx

# webserver proxy config
/bin/cp --force $appdir/src/deployment/nginx.conf /etc/nginx/nginx.conf

# celery systemd config
/bin/cp --force $appdir/src/deployment/celeryworker.service /etc/systemd/system/celeryworker.service
/bin/cp --force $appdir/src/deployment/celerybeat.service /etc/systemd/system/celerybeat.service

# app systemd config
/bin/cp --force $appdir/src/deployment/$appname.service /etc/systemd/system/$appname.service

# Give the ownership back to the app user and restart the daemons.
chown --recursive $appuser:$appuser $appdir
chmod 755 $appdir/src/deployment/app-prepare.sh

/bin/su -c "POETRY_HOME=$POETRY_HOME appdir=$appdir $appdir/src/deployment/app-prepare.sh" - $appuser

systemctl daemon-reload

systemctl enable celeryworker
systemctl enable celerybeat
systemctl enable $appname
systemctl enable nginx

# copy certificates, they should only be readable by root
cp -R $appdir/src/certificates/. $appdir/certificates
chown --recursive root:root $appdir/certificates/
chmod --recursive 400  $appdir/certificates/

# reset the selinux context for staticfiles/assets and certificates
semanage fcontext --modify --type httpd_sys_content_t "$appdir/src/assets(/.*)?" || true
semanage fcontext --modify --type httpd_sys_content_t "$appdir/certificates(/.*)?" || true
restorecon -Rv $appdir/src/assets
restorecon -Rv $appdir/certificates

systemctl restart celeryworker
systemctl restart celerybeat
systemctl restart $appname
systemctl restart nginx

# Finished :)
appversion=$(grep -m 1 -oP 'version\s*=\s*"\K[^"]+' pyproject.toml)

popd

wall "Deployed $appname=$appversion on $(lsb_release --description --short)."
