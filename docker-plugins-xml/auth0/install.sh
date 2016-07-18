#!/bin/bash

PWWD=`pwd`
cd .. && . ./docker-compose.env
cd $PWWD


if [ -f ~/.auth0.env ]; then
    scp ~/.auth0.env ${SSH_CONFIG_NAME}:/home/user
fi

scp resources/main.py ${SSH_CONFIG_NAME}:/var/www
scp resources/settings.py ${SSH_CONFIG_NAME}:/var/www
scp resources/auth ${SSH_CONFIG_NAME}:/home/user
scp resources/REQUIREMENTS.txt ${SSH_CONFIG_NAME}:/home/user
scp resources/setup-repo.sh  ${SSH_CONFIG_NAME}:/home/user


# Install all modifications and restart services
# Note: there is no difference between auth and auth-dev in this setup!
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "echo \"
/opt/venv/bin/pip install -r /home/user/REQUIREMENTS.txt
mv /home/user/auth /etc/nginx/incl.d/auth
cp /etc/nginx/incl.d/auth /etc/nginx/incl.d/auth-dev
/bin/bash chown ${SSH_USER}:users /var/www/main.py
mkdir /home/uwsgi
mv /home/user/.auth0.env /home/uwsgi
chown -R uwsgi /home/uwsgi
supervisorctl restart app-uwsgi
supervisorctl restart nginx
\" > /home/user/setup.sh"
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "sudo /bin/bash /home/user/setup.sh"
