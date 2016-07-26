#!/bin/bash
# Example run: CUSTOM_APT_CATCHER_IP=172.17.0.2 CUSTOM_HTTP_PORT=8080 CUSTOM_HTTPS_PORT=8443  ./test-run.sh load
PWWD=`pwd`

if [ -z ~/supervisor_logs ]; then
    mkdir ~/supervisor_logs
    chmod 777 ~/supervisor_logs
fi

cd ..

echo -e "\nApplying environment..."
. docker-compose.env

echo -e "\nAttempting to shutdown any existing containers/volumes..."
docker-compose down -v

set -e

echo -e "\nRunning detached containers..."
docker-compose up -d

CONTAINER_IP=`docker inspect --format "{{ .NetworkSettings.Networks.${COMPOSE_PROJECT_NAME}_default.IPAddress }}" ${COMPOSE_PROJECT_NAME}_base_1`

echo "Container IP is ${CONTAINER_IP}"
sed -i -e "s/172.[0-9]\+.0../${CONTAINER_IP}/g" ~/.ssh/config
sudo sed -i -e "s/172.[0-9]\+.0../${CONTAINER_IP}/g" /etc/hosts

cd $PWWD

# Install auth0
sleep 3
./install.sh


if [ "$1" == "load" ]; then
  echo -e "\nRemotely loading test plugins..."
  sleep 5
  ./tests/remote-load-test-plugins.sh $SSH_CONFIG_NAME
fi
