#!/bin/bash
. ../docker-compose.env
if [ -f ".env" ]; then
    scp .env ${SSH_CONFIG_NAME}:/var/www
fi
scp main.py ${SSH_CONFIG_NAME}:/var/www
scp settings.py ${SSH_CONFIG_NAME}:/var/www
scp qgis-repo.conf ${SSH_CONFIG_NAME}:/home/user
scp REQUIREMENTS.txt ${SSH_CONFIG_NAME}:/home/user
ssh ${SSH_CONFIG_NAME} "sed -i -e 's/domain-tld-dev/${DOMAIN_TLD_DEV}/g' /home/user/qgis-repo.conf"
ssh ${SSH_CONFIG_NAME} "sed -i -e 's/domain-tld/${DOMAIN_TLD}/g' /home/user/qgis-repo.conf"
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "sudo /opt/venv/bin/pip install -r /home/user/REQUIREMENTS.txt"
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "sudo mv /home/user/qgis-repo.conf /etc/nginx/conf.d/"
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "sudo supervisorctl restart app-uwsgi"
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "sudo supervisorctl restart nginx"
