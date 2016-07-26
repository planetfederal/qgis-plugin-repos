#!/bin/bash
# Test that plugins updates remove plugins when a plugin is moved from
# not-auth to auth if the version stay the same
# Example run: CUSTOM_APT_CATCHER_IP=172.17.0.2 CUSTOM_HTTP_PORT=8080 CUSTOM_HTTPS_PORT=8443 ./update_test.sh boundless.test


if [ $# -eq 0 ]; then
  echo "Usage: $0 <ssh-config-host>"
  echo "Loads test plugins into remote docker container and updates repository the run tests"
  exit 1
fi

PWWD=`pwd`
cd ../..

echo -e "\nApplying environment..."
. docker-compose.env
cd $PWWD

cd ..
./test-rebuild-run.sh
cd $PWWD

# parent directory of script
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)

cd "${SCRIPT_DIR}/../../www-data/resources/plugins-xml/uploads"

SSH_HOST="${1}"
UPLOADS="/opt/repo-updater/uploads/"
UPDATER="/opt/repo-updater/plugins-xml/plugins-xml.sh"

function upload_plugin {
  LC_ALL=C  scp $1 ${SSH_HOST}:${UPLOADS} &>/dev/null
  LC_ALL=C  ssh ${SSH_HOST} "${UPDATER} update $@ &>/dev/null"
}


function test_plugin_is_there {
    LC_ALL=C  ssh ${SSH_HOST} "ls $1 &>/dev/null"
    if [ $? -ne 0 ]; then
        echo "!!! Test failed! $1 is not there"
    else
        echo "*** Test passed. $1 is there"
    fi
}

function test_plugin_is_not_there {
    LC_ALL=C  ssh ${SSH_HOST} "ls $1 &>/dev/null"
    if [ $? -eq 0 ]; then
        echo "!!! Test failed! $1 is there"
    else
        echo "*** Test passed. $1 is not there"
    fi
}



# Clone test_plugin_1 and bump to 0.2
cp -r ../test/test_plugin_1 .
sed -i -e 's/0\.1/0.2/' ./test_plugin_1/metadata.txt
zip -r test_plugin_1-02.zip test_plugin_1 &>/dev/null

# No auth required
upload_plugin test_plugin_1.zip
# Test that the plugin is in the right place
test_plugin_is_there "/var/www/qgis/plugins/packages/test_plugin_1.0.1.zip"
test_plugin_is_not_there "/var/www/qgis/plugins/packages-auth/test_plugin_1.0.1.zip"

# Auth required
upload_plugin test_plugin_1.zip --auth
# Test that the plugin has been removed from the non-auth
test_plugin_is_not_there "/var/www/qgis/plugins/packages/test_plugin_1.0.1.zip"
# Test that the plugin is in the right place
test_plugin_is_there "/var/www/qgis/plugins/packages-auth/test_plugin_1.0.1.zip"

# No auth required
upload_plugin test_plugin_1.zip
# Test that the plugin is in the right place
test_plugin_is_there "/var/www/qgis/plugins/packages/test_plugin_1.0.1.zip"
# And it's not in the auth anymore
test_plugin_is_not_there "/var/www/qgis/plugins/packages-auth/test_plugin_1.0.1.zip"

# Upoad a new version, test if the old one is kept
upload_plugin test_plugin_1-02.zip --keep-zip
# Test that the plugin is in the right place
test_plugin_is_there "/var/www/qgis/plugins/packages/test_plugin_1-02.0.2.zip"
# Is the old one still there?
test_plugin_is_there "/var/www/qgis/plugins/packages/test_plugin_1.0.1.zip"


# Test the dev #################################################################

# No auth required
upload_plugin test_plugin_1.zip --dev
# Test that the plugin is in the right place
test_plugin_is_there "/var/www/qgis-dev/plugins/packages/test_plugin_1.0.1*.zip"
test_plugin_is_not_there "/var/www/qgis-dev/plugins/packages-auth/test_plugin_1.0.1*.zip"

# Auth required
upload_plugin test_plugin_1.zip --auth --dev
# Test that the plugin is in the right place
test_plugin_is_not_there "/var/www/qgis-dev/plugins/packages/test_plugin_1.0.1*.zip"
test_plugin_is_there "/var/www/qgis-dev/plugins/packages-auth/test_plugin_1.0.1*.zip"

# No auth required
upload_plugin test_plugin_1.zip --dev
# Test that the plugin is in the right place
test_plugin_is_there "/var/www/qgis-dev/plugins/packages/test_plugin_1.0.1*.zip"
test_plugin_is_not_there "/var/www/qgis-dev/plugins/packages-auth/test_plugin_1.0.1*.zip"

# Test if uploading the same version the previous copy is deleted
# Get the older name
OLDNAME=`LC_ALL=C  ssh boundless.test "ls /var/www/qgis-dev/plugins/packages/test_plugin_1.0.1*"`
# No auth required
upload_plugin test_plugin_1.zip --dev
# Test that the plugin is in the right place
test_plugin_is_not_there "/var/www/qgis-dev/plugins/packages/$OLDNAME"
test_plugin_is_there "/var/www/qgis-dev/plugins/packages/test_plugin_1.0.1*.zip"


# Test if upgrading the version the older versions are deleted

# Test that the old version is there
test_plugin_is_there "/var/www/qgis-dev/plugins/packages/test_plugin_1.0.1*.zip"
# Upload the new version
upload_plugin test_plugin_1-02.zip --dev
# Test that the plugin is in the right place
test_plugin_is_there "/var/www/qgis-dev/plugins/packages/test_plugin_1-02.0.2*.zip"
# Test that the old version has been deleted
test_plugin_is_not_there "/var/www/qgis-dev/plugins/packages/test_plugin_1.0.1*.zip"
