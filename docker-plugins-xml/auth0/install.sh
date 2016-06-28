#!/bin/bash

PWWD=`pwd`
cd .. && . ./docker-compose.env
cd $PWWD


if [ -f ".env" ]; then
    scp .env ${SSH_CONFIG_NAME}:/var/www
fi

scp resources/main.py ${SSH_CONFIG_NAME}:/var/www
scp resources/settings.py ${SSH_CONFIG_NAME}:/var/www
scp resources/qgis-repo.conf ${SSH_CONFIG_NAME}:/home/user
scp resources/request_methods_get-head-post ${SSH_CONFIG_NAME}:/home/user
scp resources/REQUIREMENTS.txt ${SSH_CONFIG_NAME}:/home/user
scp resources/plugins.xsl ${SSH_CONFIG_NAME}:/home/user
scp resources/plugins-dev.xsl ${SSH_CONFIG_NAME}:/home/user
# Note: this file needs to be modified by setup-repo.sh
scp resources/plugins-xml.py ${SSH_CONFIG_NAME}:/home/user
# Note: this file comes from another container and it's not in qgisrepo_base
#       need to re-run in order to make changes to plugins-xml.py
scp resources/setup-repo.sh  ${SSH_CONFIG_NAME}:/home/user

ssh ${SSH_CONFIG_NAME} "sed -i -e 's/domain-tld-dev/${DOMAIN_TLD_DEV}/g' /home/user/qgis-repo.conf"
ssh ${SSH_CONFIG_NAME} "sed -i -e 's/domain-tld/${DOMAIN_TLD}/g' /home/user/qgis-repo.conf"


# Install all modifications and restart services
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "echo \"
export SSH_USER=${SSH_USER}
export UPLOADED_BY=${UPLOADED_BY}
export DOMAIN_TLD=${DOMAIN_TLD}
export DOMAIN_TLD_DEV=${DOMAIN_TLD_DEV}
mv /home/user/plugins-xml.py /opt/repo-updater/plugins-xml/
/bin/bash /home/user/setup-repo.sh
/opt/venv/bin/pip install -r /home/user/REQUIREMENTS.txt
mv /home/user/qgis-repo.conf /etc/nginx/conf.d/
mv /home/user/request_methods_get-head-post /etc/nginx/incl.d/
mv /home/user/plugins.xsl /var/www/qgis/plugins/
mv /home/user/plugins-dev.xsl /var/www/qgis-dev/plugins/
supervisorctl restart app-uwsgi
supervisorctl restart nginx
\" > /home/user/setup.sh"
LC_ALL="C" ssh -t ${SSH_CONFIG_NAME} "sudo /bin/bash /home/user/setup.sh"
