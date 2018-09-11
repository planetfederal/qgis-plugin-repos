#!/bin/bash

QGIS_REPO=qgisrepo_base_1
QGIS_ARCHIVE=qgis-repo-www-backup_$(date +%Y%m%d-%H%M%S).tgz
ARCHIVE_DIR=$HOME/qgis-repo-backup

mkdir -p $ARCHIVE_DIR

echo -e "\nApplying environment..."
. docker-compose.env

echo -e "\nAttempting to pause running services..."
docker-compose pause

echo -e "\nAttempting to back up ${QGIS_REPO}'s /www/{qgis,qgis-dev,qgis-beta} dirs to \n$ARCHIVE_DIR/${QGIS_ARCHIVE}..."
docker run --rm --volumes-from $QGIS_REPO -v $ARCHIVE_DIR:/backup debian:stretch \
  tar -cvzf /backup/$QGIS_ARCHIVE -C / /var/www/qgis /var/www/qgis-dev /var/www/qgis-beta \
|| {
  echo -e "\n... backup failed"
  docker-compose unpause
  exit 1
}

if [ ! -f $ARCHIVE_DIR/$QGIS_ARCHIVE ]; then
  echo -e "\n... backup failed"
  docker-compose unpause
  exit 1
fi

echo -e "\nAttempting to unpause running services..."
docker-compose unpause

echo -e "\nAttempting to shutdown existing containers/volumes..."
docker-compose down -v

set -e

echo -e "\nBuilding container images..."
docker-compose build

echo -e "\nRunning detached containers..."
docker-compose up -d

echo -e "\nAttempting to restore $ARCHIVE_DIR/${QGIS_ARCHIVE} to ${QGIS_REPO}..."
docker run --rm --volumes-from $QGIS_REPO -v $ARCHIVE_DIR:/backup debian:stretch \
  tar -xvf /backup/$QGIS_ARCHIVE -C /
