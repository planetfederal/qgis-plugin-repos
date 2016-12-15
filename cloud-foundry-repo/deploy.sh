#!/bin/bash

# Deploy the project on PCF

TMP_DIR=tmp
USERNAME=${1:-admin}
PASSWORD=${2:-password}

if [ -d $TMP_DIR ]; then
    rm -rf $TMP_DIR
fi

pushd .

mkdir $TMP_DIR

cp -r -L plugins_* $TMP_DIR
cp manifest.yml $TMP_DIR
sed -i -e "s/USERNAME: admin/USERNAME: ${USERNAME}/" $TMP_DIR/manifest.yml
sed -i -e "s/PASSWORD: password/PASSWORD: ${PASSWORD}/" $TMP_DIR/manifest.yml
cd $TMP_DIR
cf push

popd
