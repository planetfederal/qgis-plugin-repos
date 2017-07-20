#!/bin/bash

set -e

cd /opt/setup

### Supervisor ###

mkdir -p /var/log/supervisor
cp services.conf /etc/supervisor/conf.d/
sed -i "s@uid user@uid ${SSH_USER}@g" /etc/supervisor/conf.d/services.conf
cat supervisord.conf > /etc/supervisor/supervisord.conf


### SSH ###

mkdir /var/run/sshd

# Make a subdir for sshd config that can be overlaid from services-conf,
# without affecting generated keypairs
mkdir /etc/ssh/sshd
mv /etc/ssh/sshd_config /etc/ssh/sshd/
ln -fs sshd/sshd_config /etc/ssh/sshd_config


### Python ###

pushd /opt > /dev/null

    if [ ! -d venv ]; then
      pip install virtualenv
      virtualenv --system-site-packages venv
    fi
    # Install any requirements.txt
    . venv/bin/activate
    pip install flask

popd  > /dev/null #/opt

chown -R ${SSH_USER}:users /opt

# Use 2048 bit Diffie-Hellman RSA key parameters
# (otherwise Nginx defaults to 1024 bit, lowering the strength of encryption # when using PFS)
# NOTE: this takes a minute or two
# See: https://juliansimioni.com/blog/https-on-nginx-from-zero-to-a-plus-part-2-configuration-ciphersuites-and-performance/
# Note that we need to use a directory that is not overlaid by other docker volumes!
NGINX_SSL=/etc/nginx-no-overlay/ssl
mkdir -p $NGINX_SSL
openssl dhparam -outform pem -out $NGINX_SSL/dhparam2048.pem 2048
chmod go-r $NGINX_SSL/dhparam2048.pem
