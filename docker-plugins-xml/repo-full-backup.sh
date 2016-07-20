#!/bin/bash

QGIS_BASE=qgisrepo_base_1
QGIS_CONF=qgisrepo_conf_1
QGIS_REPO=qgisrepo_data_1
QGIS_ARCHIVE=qgis-repo-full-backup_$(date +%Y%m%d-%H%M%S).tgz
ARCHIVE_DIR=$HOME/qgis-repo-backup

mkdir -p $ARCHIVE_DIR

echo -e "\nApplying environment..."
. docker-compose.env

echo -e "\nAttempting to pause running services..."
docker-compose pause

echo -e "\nAttempting to back up ${QGIS_REPO}'s /www/{qgis,qgis-dev} dirs to \n$ARCHIVE_DIR/${QGIS_ARCHIVE}..."
docker run --rm \
--volumes-from $QGIS_BASE --volumes-from $QGIS_CONF --volumes-from $QGIS_REPO \
-v $ARCHIVE_DIR:/backup debian:jessie \
  tar --ignore-failed-read -cvzf /backup/$QGIS_ARCHIVE -C / \
  /home/${SSH_USER} \
  /etc/nginx \
  /etc/ssh \
  /etc/ssl/nginx \
  /etc/supervisor \
  /etc/uwsgi \
  /opt \
  /usr/lib/nginx \
  /var/www

if [ ! -f $ARCHIVE_DIR/$QGIS_ARCHIVE ]; then
  echo -e "\n... backup failed"
fi

echo -e "\nAttempting to unpause running services..."
docker-compose unpause
