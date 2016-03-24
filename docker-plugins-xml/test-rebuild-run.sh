#!/bin/bash

echo -e "\nApplying environment..."
. docker-compose.env

echo -e "\nAttempting to shutdown any existing containers/volumes..."
docker-compose down -v

set -e

echo -e "\nBuilding container images..."
docker-compose build

echo -e "\nRunning detached containers..."
docker-compose up -d

if [ "$1" == "load" ]; then
  echo -e "\nRemotely loading test plugins..."
  sleep 5
  ./www-data/resources/plugins-xml/test/remote-load-test-plugins.sh $SSH_CONFIG_NAME
fi
