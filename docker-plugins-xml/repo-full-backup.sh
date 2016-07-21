#!/bin/bash

set -e

QGIS_BASE=qgisrepo_base_1
QGIS_ARCHIVE=qgis-repo-full-backup_$(date +%Y%m%d-%H%M%S).tgz
ARCHIVE_DIR=$HOME/qgis-repo-backup

mkdir -p $ARCHIVE_DIR

echo -e "\nApplying environment..."
. docker-compose.env

echo -e "\nAttempting to back up ${QGIS_BASE}'s dirs with data to \n$ARCHIVE_DIR/${QGIS_ARCHIVE}..."
docker exec $QGIS_BASE \
tar -C / -cf - \
  home/${SSH_USER} \
  etc/nginx \
  etc/ssh \
  etc/ssl/nginx \
  etc/supervisor \
  etc/uwsgi \
  opt \
  usr/lib/nginx \
  /var/www \
| gzip > $ARCHIVE_DIR/$QGIS_ARCHIVE

if [ ! -f $ARCHIVE_DIR/$QGIS_ARCHIVE ]; then
  echo -e "\n... backup failed"
fi
