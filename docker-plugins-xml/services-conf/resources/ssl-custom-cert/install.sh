#!/bin/bash

set -ex


if [ -z $DOMAIN_TLD_DEV ]; then
  PWWD=`pwd`
  cd ../../../.. && . ./docker-compose.env
  cd $PWWD
fi 

QGIS_BASE=qgisrepo_base_1

if [ "${SSL_CUSTOM_CERT}" = "1" ]; then

  for ext in 'crt' 'key'; do
    pki=qgisrepo-server.${ext}
    if [ -f ${HOME}/.${pki} ]; then
      docker cp -L ${HOME}/.${pki} ${QGIS_BASE}:/etc/ssl/nginx/${pki}
    fi
  done

  docker exec -i ${QGIS_BASE} bash <<EOF
cd /etc/ssl/nginx/
chown -f root:root qgisrepo-server* || true
chmod -f 0600 qgisrepo-server* || true
EOF

fi

if [ "${SSL_LETSENCRYPT_CERTS}" = "1" ]; then

  # Let's Encrypt
  docker exec -i ${QGIS_BASE} bash <<EOF
sed -i \
-e 's|\(include incl\.d/ssl_cert_dev;\)|#\1|g' \
-e 's|# *\(include incl\.d/ssl_cert_letsencrypt_dev;\)|\1|g' \
-e 's|\(include incl\.d/ssl_cert_beta;\)|#\1|g' \
-e 's|# *\(include incl\.d/ssl_cert_letsencrypt_beta;\)|\1|g' \
/etc/nginx/conf.d/qgis-repo.conf

certbot certonly -a webroot --webroot-path=/var/www/qgis-dev -d ${DOMAIN_TLD_DEV}
certbot certonly -a webroot --webroot-path=/var/www/qgis-beta -d ${DOMAIN_TLD_BETA} 
EOF


  docker exec -i ${QGIS_BASE} bash <<EOF
supervisorctl restart nginx
EOF

fi
