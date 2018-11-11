#!/bin/sh

set -e

### WWW ###

WWW_DIR=/var/www

mkdir -p $WWW_DIR

# Set up skeleton of plugin repo, to be overlaid with httpd-data volume

for subdir in 'qgis' 'qgis-dev' 'qgis-beta'; do
  mkdir -p $WWW_DIR/$subdir/plugins/packages
  mkdir -p $WWW_DIR/$subdir/.well-known
  mkdir -p $WWW_DIR/$subdir/plugins/packages-auth
  touch $WWW_DIR/$subdir/index.html
  touch $WWW_DIR/$subdir/plugins/index.html
  ln -sf plugins/plugins.xml $WWW_DIR/$subdir/plugins.xml
done

chmod -R 0755 $WWW_DIR
chown -R ${SSH_USER}:users $WWW_DIR

### Repo update script ###

REPO_UPDATER=/opt/repo-updater
PLUGINS_XML=$REPO_UPDATER/plugins-xml
UPDATE_SCRIPT=$PLUGINS_XML/scripts/plugins-xml.py
UPDATE_WRAPPER=$PLUGINS_XML/scripts/plugins-xml.sh
SETTINGS_FILE_TEMPL=$PLUGINS_XML/scripts/settings.py.tmpl
SETTINGS_FILE=$PLUGINS_XML/scripts/settings.py
PY_VENV=/opt/venv

mkdir -p $REPO_UPDATER/uploads

mv /opt/setup/plugins-xml $PLUGINS_XML

# Support older script filesystem layout
# (path in .travis.yml encrypted env var data in many plugin's CI)
ln -sf scripts/plugins-xml.sh ${PLUGINS_XML}/plugins-xml.sh

# Save the settings in /opt/repo-updater/plugins-xml/scripts/settings.py
# overwrite existing settings.py
cp -f "${SETTINGS_FILE_TEMPL}" "${SETTINGS_FILE}"

# Order matters !!!
sed -i "s@WWW_DIR@${WWW_DIR}@g" ${SETTINGS_FILE}
sed -i "s@REPO_UPDATER@${REPO_UPDATER}@g" ${SETTINGS_FILE}
sed -i "s/UPLOADER/${UPLOADED_BY}/g" ${SETTINGS_FILE}
sed -i "s/DOMAIN_TLD_MIRROR/${DOMAIN_TLD_MIRROR}/g" ${SETTINGS_FILE}
sed -i "s/DOMAIN_TLD_BETA/${DOMAIN_TLD_BETA}/g" ${SETTINGS_FILE}
sed -i "s/DOMAIN_TLD_DEV/${DOMAIN_TLD_DEV}/g" ${SETTINGS_FILE}
sed -i "s/DOMAIN_TLD/${DOMAIN_TLD}/g" ${SETTINGS_FILE}

# Set the venv to use
sed -i "s@venv@${PY_VENV}@g" ${UPDATE_WRAPPER}

chown -R ${SSH_USER}:users ${REPO_UPDATER}


### Copy flask app main.py ###
FLASK_APP_FOLDER=$PLUGINS_XML/flask_app
cp $FLASK_APP_FOLDER/main.py $WWW_DIR

chown ${SSH_USER}:users $WWW_DIR/main.py
