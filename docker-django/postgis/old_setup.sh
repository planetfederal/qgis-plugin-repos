#!/bin/bash

set -e

cat /tmp/pg_hba.conf > /etc/postgresql/9.3/main/pg_hba.conf && rm /tmp/pg_hba.conf

# echo "localhost:5432:*:docker:docker" > ~/.pgpass

# PGPASSWORD=docker
# export PGPASSWORD

# Make sure we have a user set up
if [ -z "$POSTGRES_USER" ]; then
  POSTGRES_USER=docker
fi  
if [ -z "$POSTGRES_PASS" ]; then
  POSTGRES_PASS=docker
fi 

DATADIR="/var/lib/postgresql/9.3/main"
CONF="/etc/postgresql/9.3/main/postgresql.conf"
POSTGRES="/usr/lib/postgresql/9.3/bin/postgres"
INITDB="/usr/lib/postgresql/9.3/bin/initdb"
SQLDIR="/usr/share/postgresql/9.3/contrib/postgis-2.1/"

su - postgres -c "$POSTGRES -D $DATADIR -c config_file=$CONF &"

# Wait for the db to start up before trying to use it....
sleep 10

# This should show up in docker logs afterwards
# su - postgres -c "psql -l"

# su - postgres -c "createdb qgis-django"
su - postgres -c "createdb -O $POSTGRES_USER -T template_postgis qgis-django"
# su - postgres -c "createlang plpgsql qgis-django"
su - postgres -c "psql qgis-django < $SQLDIR/postgis.sql"
su - postgres -c "psql qgis-django < $SQLDIR/spatial_ref_sys.sql"

PID=$(cat /var/run/postgresql/9.3-main.pid)
kill -9 ${PID}
