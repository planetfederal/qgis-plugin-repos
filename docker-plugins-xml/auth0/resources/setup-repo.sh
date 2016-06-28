#!/bin/sh

set -e

### WWW ###

WWW_DIR=/var/www

REPO_UPDATER=/opt/repo-updater
PLUGINS_XML=$REPO_UPDATER/plugins-xml
UPDATE_SCRIPT=$PLUGINS_XML/plugins-xml.py

sed -i "s@= WEB_BASE_TEST@= '${WWW_DIR}'@g" ${UPDATE_SCRIPT}

sed -i "s@= UPLOAD_BASE_TEST@= '${REPO_UPDATER}'@g" ${UPDATE_SCRIPT}

sed -i "s@= UPLOADED_BY_TEST@= '${UPLOADED_BY}'@g" ${UPDATE_SCRIPT}

sed -i "s@= DOMAIN_TLD_TEST@= '${DOMAIN_TLD}'@g" ${UPDATE_SCRIPT}

sed -i "s@= DOMAIN_TLD_DEV_TEST@= '${DOMAIN_TLD_DEV}'@g" ${UPDATE_SCRIPT}


chown -R ${SSH_USER}:users $REPO_UPDATER

chown ${SSH_USER}:users $WWW_DIR/main.py
