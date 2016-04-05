#!/bin/sh

set -e

cd /opt/setup

### SSH ###

# Configure SSH user
rm test-ssh-keypair/boundless_test_id_rsa
mkdir -p /home/${SSH_USER}/.ssh
chmod -v 0700 /home/${SSH_USER}/.ssh
if [ -z "${SSH_PUBLIC_KEY}" ] || [ "${SSH_PUBLIC_KEY}" = "None" ]; then
  SSH_PUBLIC_KEY="$(cat test-ssh-keypair/boundless_test_id_rsa.pub)"
fi
echo "${SSH_PUBLIC_KEY}" > /home/${SSH_USER}/.ssh/authorized_keys
chmod -v 0600 /home/${SSH_USER}/.ssh/authorized_keys
chown -R ${SSH_USER}:users /home/${SSH_USER}

# Configure SSH server
mkdir -p /etc/ssh/sshd
mv sshd_config /etc/ssh/sshd/sshd_config


### Nginx ###

# Configure Nginx
NGINX_CONF=/etc/nginx
mv /opt/setup/nginx $NGINX_CONF

# Check for any custom SSL cert/key
SSL_CERT=$NGINX_CONF/ssl-test/boundless-server.crt
SSL_KEY=$NGINX_CONF/ssl-test/boundless-server.key

cd /opt/setup/ssl-custom-cert

SSL_NGINX=/etc/ssl/nginx
mkdir -p $SSL_NGINX

if [ -n "${SSL_CUSTOM_CERT}" ] && \
   [ "${SSL_CUSTOM_CERT}" != "None" ]  && \
   [ -f ./qgisrepo-server.crt ] && \
   [ -f ./qgisrepo-server.key ]; then
  cp ./qgisrepo-server.* $SSL_NGINX/
  chmod go-rwx $SSL_NGINX/qgisrepo-server.key
  SSL_CERT=$SSL_NGINX/qgisrepo-server.crt
  SSL_KEY=$SSL_NGINX/qgisrepo-server.key
fi

cd $NGINX_CONF

ln -fs /usr/lib/nginx/modules modules

# chmod o-rwx $NGINX_CONF/htpasswd

cd $NGINX_CONF/incl.d

sed -i "s#SSL_CERT#${SSL_CERT}#g" ssl_cert
sed -i "s#SSL_KEY#${SSL_KEY}#g" ssl_cert

cd $NGINX_CONF/conf.d

sed -i "s/domain-tld-dev/${DOMAIN_TLD_DEV}/g" qgis-repo.conf
sed -i "s/domain-tld/${DOMAIN_TLD}/g" qgis-repo.conf
