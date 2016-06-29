#!/bin/bash
# Example run:
# CUSTOM_APT_CATCHER_IP=172.17.0.2 CUSTOM_HTTP_PORT=8080 CUSTOM_HTTPS_PORT=8443 ./test-rebuild-run.sh load
PWWD=`pwd`


echo -e "\nApplying environment..."
cd .. && . docker-compose.env
cd  $PWWD

echo -e "\nAttempting to shutdown any existing containers/volumes..."
cd .. && docker-compose down -v
cd  $PWWD

set -e

echo -e "\nBuilding container images..."
cd .. && docker-compose build
cd  $PWWD

echo -e "\nRunning detached containers..."
cd .. && docker-compose up -d
cd  $PWWD

CONTAINER_IP=`docker inspect --format "{{ .NetworkSettings.Networks.${COMPOSE_PROJECT_NAME}_default.IPAddress }}" ${COMPOSE_PROJECT_NAME}_base_1`

echo "Container IP is ${CONTAINER_IP}"
sed -i -e "s/172.[0-9]\+.0../${CONTAINER_IP}/g" ~/.ssh/config
sudo sed -i -e "s/172.[0-9]\+.0../${CONTAINER_IP}/g" /etc/hosts


sleep 5
./install.sh

if [ "$1" == "load" ]; then
  echo -e "\nRemotely loading test plugins..."
  sleep 5
  ./tests/remote-load-test-plugins.sh $SSH_CONFIG_NAME
fi
