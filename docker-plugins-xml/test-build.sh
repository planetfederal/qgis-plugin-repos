#!/bin/bash

if [ -z ~/supervisor_logs ]; then
    mkdir ~/supervisor_logs
    chmod 777 ~/supervisor_logs
fi

echo -e "\nApplying environment..."
. docker-compose.env

echo -e "\nAttempting to shutdown any existing containers/volumes..."
docker-compose down -v

set -e

echo -e "\nBuilding container images..."
docker-compose build
