#!/bin/bash

set -e

pushd /opt

  ### django app requirements ###

  if [ ! -d QGIS-Django ]; then
    git clone https://github.com/qgis/QGIS-Django.git
  else
    cd QGIS-Django
    git clean -xdf
    git reset --hard HEAD
    git pull origin master
  fi

  pushd QGIS-Django

    # Pillow replaces PIL
    sed -i s/PIL==1.1.7/Pillow==1.7.8/g REQUIREMENTS.txt
    sed -i s/django-debug-toolbar==1.0.1/django-debug-toolbar==1.3.2/g REQUIREMENTS.txt

    if [ ! -d venv ]; then
      easy_install virtualenv
      virtualenv venv
    fi
    . venv/bin/activate
    pip install -r REQUIREMENTS.txt

  popd #QGIS-Django

popd #/opt
