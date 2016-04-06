#!/bin/bash

set -e

cd /opt/setup

### Supervisor ###

mkdir -p /var/log/supervisor
cp services.conf /etc/supervisor/conf.d/
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
