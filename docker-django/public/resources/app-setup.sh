#!/bin/bash

set -e

pushd /opt/QGIS-Django

  ### postgres/postgis setup ###
  
#   cat /opt/createdb.sh > ./createdb.sh && rm /opt/createdb.sh
#   chmod 0700 ./createdb.sh
#   ./createdb.sh
  
  pushd qgis-app
  
    mv /opt/settings_local.py ./
    
    . ../venv/bin/activate
    
    python manage.py migrate auth
    python manage.py migrate contenttypes
    python manage.py migrate sites
    
    python manage.py migrate
    
#     python manage.py makemigrations
# 
#     python manage.py migrate
  
#     python manage.py syncdb
    
  popd #qgis-app

popd #QGIS-Django
