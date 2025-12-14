#!/bin/bash

# Installing pytomatom - including deploy dependencies - on the server, manually.
# ! Don't run this as a script, but copy-paste the commands one by one, so you can check the output and errors.


# === PREPARATION - adminuser & ssh setup =====================================
# Update Subscription Management repositories.
# working as root
sudo su

dnf clean all
dnf update

# --- SELXINUX ----------------------------------------------------------------
# FIXME: caution, this will DISABLE the security tool selinux for this application
# I don't reocmmend doing this, but until the context for this application is
# st correctly and fixed during the deployment this is the only way currently
# to make to application run without issues.
# ->
# nano /etc/sysconfig/selinux
# # SELINUX=enforcing -> SELINUX=permissive
# -----------------------------------------------------------------------------


# Add a new administrator user, that is shared and has some keys to login
# CAVEAT: most of the packages, that install to the userspace have to be copied for every other user otherwise.
adminuserandgroup=sgadmin
adminuserandgroupid=1337
(
    echo "adminuserandgroup=$adminuserandgroup"
    echo "adminuserandgroupid=$adminuserandgroupid"
) | tee --append /etc/profile.d/admingroupandunser.sh >/dev/null
source /etc/profile.d/admingroupandunser.sh

# Check if gid or user are present in /etc/group, if not, create
! cat /etc/group | grep $adminuserandgroupid \
    && ! cat /etc/group | grep $adminuserandgroup \
    && groupadd --gid $adminuserandgroupid $adminuserandgroup \
    && useradd \
        --gid $adminuserandgroupid \
        --uid $adminuserandgroupid \
        --home /home/$adminuserandgroup \
        --shell /bin/bash $adminuserandgroup \
        --comment "sg.digital adminuser $adminuserandgroup" \
    && mkdir --parents /home/$adminuserandgroup/.ssh \
    && touch /home/$adminuserandgroup/.ssh/authorized_keys \
    && usermod --append --groups wheel $adminuserandgroup

# ! TODO: add your public key to the authorized_keys file, don't mess this up, or login will be impossible ;-)
# echo SSH_KEY_PYTOMATOM_PRODUCTION_id_rsa.pub | tee --append /home/$adminuserandgroup/.ssh/authorized_keys
chmod 700 /home/$adminuserandgroup/.ssh
chmod 600 /home/$adminuserandgroup/.ssh/authorized_keys
chown -R $adminuserandgroup:$adminuserandgroup /home/$adminuserandgroup
# Disallow password login for all other users if a public key is present in the authorized_keys file
cat /home/$adminuserandgroup/.ssh/authorized_keys \
    && sed --in-place 's/^#*PasswordAuthentication.*/PasswordAuthentication no/; s/^#*PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config \
    && systemctl restart sshd

exit


# === INSTALLATION ============================================================
# Login with the new user
# should be set inside your ~/.ssh/config according to the README example.
ssh pytomatom
# ...
# working as root
sudo su


# Finding installed RHEL version
dnf whatprovides lsb_release
dnf install redhat-lsb-core --assumeyes
wall "Deploying pytomatom on $(lsb_release --description --short)"
# At the time of writing
# $(lsb_release --id --short) == RedHatEnterprise
# $(lsb_release --release --short) == 8.8
# $(lsb_release --codename --short) == Ootpa

# To have a broader sudo timeout during setup, ! TEMPORARILY ! change the following line in /etc/sudoers with visudo
# sudo visudo
# --
# Defaults        env_reset,timestamp_timeout=20
# --

# --- INSTALL SETUP DEPENDENCIES ----------------------------------------------
dnf install git --assumeyes
dnf install jq --assumeyes

# --- APP SPECIFIC VARIABLES --------------------------------------------------
appuser=app
appname=app
appid=2001
appdir=/$appname
(
    echo "appuser=$appuser"
    echo "appname=$appname"
    echo "appid=$appid"
    echo "appdir=$appdir"
) | sudo tee --append /etc/profile.d/app.sh >/dev/null
source /etc/profile.d/app.sh

# --- INSTALL POSTGRES (database) ---------------------------------------------
# Installing postgres
dnf install https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm --assumeyes
dnf module disable postgresql --quiet --assumeyes
dnf install postgresql15-server --assumeyes
/usr/pgsql-15/bin/postgresql-15-setup initdb
systemctl enable postgresql-15
systemctl start postgresql-15


# --- INSTALL REDIS (key-value-store) -----------------------------------------
# Find out what version-streams are available.
# sudo dnf module list redis
dnf module reset redis
dnf module install redis:7 --assumeyes  # 7 might not be available yet, use the latest available


# --- INSTALL PYTHON (backend language) ---------------------------------------
# Install python build dependencies (C build, gcc etc.)
dnf groupinstall "Development Tools" --assumeyes
dnf install bzip2-devel ncurses-devel readline-devel sqlite-devel libffi-devel --assumeyes

# Install pyenv
(
    echo '#!/bin/bash'
    echo 'export PYENV_ROOT="/opt/pyenv"'
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"'
    echo 'if command -v pyenv &> /dev/null'
    echo 'then'
    echo '    eval "$(pyenv init - --no-rehash)"'
    echo '    eval "$(pyenv virtualenv-init -)"'
    echo '    pyenv rehash 2>/dev/null'
    echo 'fi'
) | tee --append /etc/profile.d/pyenv.sh >/dev/null

source /etc/profile.d/pyenv.sh
curl https://pyenv.run | bash

# Use python 3.11
pythonminorversion=3.11

# Install latest python via pyenv
pythonversion=$(pyenv install --list | grep $pythonminorversion | sort -t. -k1,1n -k2,2n -k3,3n | tail -n1 | tr -d ' ')

# Pick the latest bugfix release
echo "pythonversion=$pythonversion" | tee --append /etc/profile.d/pythonversion.sh >/dev/null
pyenv install $pythonversion
pyenv global $pythonversion


# Install poetry
POETRY_HOME=/opt/poetry
(
    echo 'POETRY_HOME=/opt/poetry'
    echo 'PATH=$POETRY_HOME/bin:$PATH'
) | tee --append /etc/profile.d/poetry.sh >/dev/null

mkdir --parents $POETRY_HOME
curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python -
# curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python - --uninstall

$POETRY_HOME/bin/poetry config virtualenvs.in-project true
$POETRY_HOME/bin/poetry config cache-dir $POETRY_HOME/.cache
rm -rf /root/.cache/pypoetry
$POETRY_HOME/bin/poetry self update

# --- INSTALL YARN (frontend langauge) ----------------------------------------
# Add node.js and yarn to the repositories & install.
# Find out what version-streams are available.
# dnf module list nodejs
# If neccecary, reset the module to the default stream.
dnf module reset nodejs
# Then update the module to use the latest available stream and install the version you want.
dnf module install nodejs:18 --assumeyes
# Add yarn..
curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | tee /etc/yum.repos.d/yarn.repo
dnf install yarn --assumeyes


# --- INSTALL DOPPLER (env secrets management) --------------------------------
rpm --import 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key'
curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/config.rpm.txt' | tee /etc/yum.repos.d/doppler-cli.repo
dnf update --assumeyes && dnf install doppler --assumeyes
doppler update

# Prevent the token being leaked in bash history
export HISTIGNORE='export DOPPLER_TOKEN*'
# ! TODO: add the doppler token for the app here
export DOPPLER_TOKEN='dp.st.prd.xxxx'
# ! Also add the token to the env, for the deployment pipeline scripts to work automated.
echo $DOPPLER_TOKEN > /root/.doppler/$appname-token

# --- INSTALL THE APP ---------------------------------------------------------
# Create the app's directory, the app's group and user and set the permissions

# Check if gid or user are present in /etc/group
! cat /etc/group | grep $appid && ! cat /etc/group | grep $appuser && groupadd --gid $appid $appuser
usermod --append --groups $adminuserandgroup $appuser

mkdir --parents $appdir
mkdir --parents $appdir/certificates
useradd --gid $appid --uid $appid --home $appdir -M --shell /bin/bash $appuser --comment "webappuser $appuser"
echo 'PATH=$appdir/src/.venv/bin:$PATH' | tee --append $appdir/.bash_profile
echo 'export DJANGO_SETTINGS_MODULE=config.settings.production' | tee --append $appdir/.bash_profile
echo 'cd src' | tee --append $appdir/.bash_profile

chown --recursive $appuser:$appuser $appdir
git config --global --add safe.directory $appdir/src


# --- PREPARE THE POSTGRES DATABASES ------------------------------------------
# Know the database password and dbusername and dbname you entered in the
# doppler secrets (or create them now)
doppler secrets download --format=json --no-file --config=production | jq

sudo -i -u postgres
psql
# ! add the doppler secrets for postgres variable 'desired_password' here.
CREATE USER pytomatomproduser WITH PASSWORD 'desired_password';
CREATE DATABASE pytomatomproddb;
ALTER DATABASE pytomatomproddb OWNER TO pytomatomproduser;
GRANT ALL PRIVILEGES ON DATABASE pytomatomproddb TO pytomatomproduser;
\q
exit


# --- CONFIGURE REDIS ---------------------------------------------------------
systemctl enable redis
systemctl start redis

export HISTIGNORE='REDIS_PASSWORD*'
# set REDIS_PASSWORD -> from doppler envs
REDIS_PASSWORD=$(doppler secrets download --format=json --no-file --config=production | jq -r '.REDIS_PASSWORD') \
    # && sed --in-place "s|ExecStart=/usr/bin/redis-server /etc/redis\.conf --daemonize no --supervised systemd|ExecStart=/usr/bin/redis-server /etc/redis\.conf --daemonize no --supervised systemd --requirepass ${REDIS_PASSWORD}|" /usr/lib/systemd/system/redis.service \
    # TODO: find out wheter to actively comment out ExecStart=... in /usr/lib/systemd/system/redis.service, probably that should be done at least once
    && echo -e "[Service]\nExecStart=/usr/bin/redis-server /etc/redis.conf --daemonize no --supervised systemd --requirepass ${REDIS_PASSWORD}" | tee /etc/systemd/system/redis.service.d/startup.conf > /dev/null && chmod 644 /etc/systemd/system/redis.service.d/startup.conf
    && systemctl daemon-reload
    && systemctl restart redis
# We replaced doing changes in /etc/redis.conf with doing changes in the
# redis.service file and the --requirepass option, because conf entry-passwords will be deprecated soon.
# && sed --in-place "s/^# requirepass .*/requirepass ${REDIS_PASSWORD}/;" /etc/redis.conf \


# --- SETUP THE WEBSERVER -----------------------------------------------------
dnf install nginx --assumeyes

systemctl start nginx
systemctl enable nginx


# --- RE-DEPLOY THE APP -------------------------------------------------------
export HISTIGNORE='DEPLOYMENT_TOKEN*'
# set DEPLOYMENT_TOKEN -> from doppler envs
DEPLOYMENT_TOKEN=$(doppler secrets download --format=json --no-file --config=production | jq -r '.DEPLOYMENT_TOKEN')
GITHUB_REPO_URL=https://machine-sgdigital:$DEPLOYMENT_TOKEN@github.com/061-Digital-IT-Germany-Austria/pytomatom

# clone once beforehand
export HISTIGNORE='git clone*'
[ -z "$(ls -A $appdir/src)" ] && git clone $GITHUB_REPO_URL $appdir/src || echo "Directory $appdir/src is not empty. Skipping cloning."
# set the secontext for the appdir once beforehand
semanage fcontext --add --type httpd_sys_content_t "$appdir/src/assets(/.*)?"
semanage fcontext --add --type httpd_sys_content_t "$appdir/certificates(/.*)?"
restorecon -Rv $appdir/src/assets
restorecon -Rv $appdir/certificates




chmod +x $appdir/src/deployment/app-prepare.sh"
chmod +x $appdir/src/deployment/app-deploy.sh
chmod +x $appdir/src/deployment/app-deploy-pipeline.sh"

mkdir --parents /opt/bin
/bin/cp --force $appdir/src/deployment/app-deploy-pipeline.sh /opt/bin/app-deploy-pipeline.sh
chmod +x /opt/bin/app-deploy-pipeline.sh

# ! This shall be the redeploy script-part

# ... see app-deploy-pipeline.sh
DOPPLER_TOKEN=$DOPPLER_TOKEN \
GITHUB_REPO_URL=$GITHUB_REPO_URL \
adminuserandgroup=$adminuserandgroup \
POETRY_HOME=$POETRY_HOME \
appuser=$appuser \
appname=$appname \
appdir=$appdir \
/opt/bin/app-deploy-pipeline.sh
