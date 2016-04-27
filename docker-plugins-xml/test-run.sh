#!/bin/bash

echo -e "\nApplying environment..."
. docker-compose.env

echo -e "\nAttempting to shutdown any existing containers/volumes..."
docker-compose down -v

set -e

echo -e "\nRunning detached containers..."
docker-compose up -d

CONTAINER_IP=`docker inspect --format '{{ .NetworkSettings.Networks.qgisrepo_default.IPAddress }}' qgisrepo_base_1`

sed -i -e "s/172.18.0../${CONTAINER_IP}/g" ~/.ssh/config
sudo sed -i -e "s/172.18.0../${CONTAINER_IP}/g" /etc/hosts

if [ "$1" == "load" ]; then
  echo -e "\nRemotely loading test plugins..."
  sleep 5
  ./www-data/resources/plugins-xml/test/remote-load-test-plugins.sh $SSH_CONFIG_NAME
fi
