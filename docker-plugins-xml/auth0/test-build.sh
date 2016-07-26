#!/bin/bash
# Example run:
# CUSTOM_APT_CATCHER_IP=172.17.0.2 CUSTOM_HTTP_PORT=8080 CUSTOM_HTTPS_PORT=8443 ./test-build.sh load
PWWD=`pwd`


if [ -z ~/supervisor_logs ]; then
    mkdir ~/supervisor_logs
    chmod 777 ~/supervisor_logs
fi


echo -e "\nApplying environment..."
cd .. && . ./docker-compose.env
cd $PWWD

echo -e "\nAttempting to shutdown any existing containers/volumes..."
cd .. && docker-compose down -v
cd $PWWD

set -e

echo -e "\nBuilding container images..."
cd .. && docker-compose build
cd $PWWD


echo -e "\nRunning detached containers..."
cd .. && docker-compose up -d
cd $PWWD

# Install auth0
sleep 3
./install.sh


if [ "$1" == "load" ]; then
  echo -e "\nRemotely loading test plugins..."
  sleep 5
  ./tests/remote-load-test-plugins.sh $SSH_CONFIG_NAME
fi

echo -e "\nAttempting to shutdown any existing containers/volumes..."
cd .. && docker-compose down -v
cd  $PWWD
