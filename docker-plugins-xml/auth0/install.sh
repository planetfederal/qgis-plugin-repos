#!/bin/bash

set -ex

PWWD=`pwd`
cd .. && . ./docker-compose.env
cd $PWWD


if [ -f ~/.auth0.env ]; then
    scp ~/.auth0.env ${SSH_CONFIG_NAME}:/home/${SSH_USER}
fi

scp resources/auth.py ${SSH_CONFIG_NAME}:/var/www
scp resources/settings.py ${SSH_CONFIG_NAME}:/var/www
scp resources/auth ${SSH_CONFIG_NAME}:/home/${SSH_USER}
scp resources/api ${SSH_CONFIG_NAME}:/home/${SSH_USER}
scp resources/REQUIREMENTS.txt ${SSH_CONFIG_NAME}:/home/${SSH_USER}
#scp resources/setup-repo.sh  ${SSH_CONFIG_NAME}:/home/${SSH_USER}


# Install all modifications and restart services
# Note: there is no difference between auth and auth-dev or auth-beta in this setup!
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "echo \"
/opt/venv/bin/pip install -r /home/${SSH_USER}/REQUIREMENTS.txt
mv /home/${SSH_USER}/auth /etc/nginx/incl.d/auth
cp /etc/nginx/incl.d/auth /etc/nginx/incl.d/auth-dev
cp /etc/nginx/incl.d/auth /etc/nginx/incl.d/auth-beta
mv /home/${SSH_USER}/api /etc/nginx/incl.d/api
cp /etc/nginx/incl.d/api /etc/nginx/incl.d/api-dev
cp /etc/nginx/incl.d/api /etc/nginx/incl.d/api-beta
chown ${SSH_USER}:users /var/www/auth.py
mkdir /home/uwsgi
mv /home/${SSH_USER}/.auth0.env /home/uwsgi
chown -R uwsgi /home/uwsgi
supervisorctl restart app-uwsgi
supervisorctl restart nginx
\" > /home/${SSH_USER}/setup.sh"
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "sudo /bin/bash /home/${SSH_USER}/setup.sh"
