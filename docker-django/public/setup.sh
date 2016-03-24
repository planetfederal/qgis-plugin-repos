#!/bin/bash

# Bug fix: https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1325142/comments/38
dpkg-divert --local --add /etc/init.d/systemd-logind \
 && ln -s /bin/true /etc/init.d/systemd-logind

# Use apt-catcher-ng caching
echo 'Acquire::http { Proxy "http://'${APT_CATCHER_IP}':3142"; };' >> /etc/apt/apt.conf.d/01proxy

# Avoid 'ERROR: invoke-rc.d: policy-rc.d denied execution'
echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d

apt-get -q -y update

DEBIAN_FRONTEND=noninteractive apt-get -q -y install git \
  python-dev \
  python-setuptools \
  python-pip \
  libldap2-dev \
  libsasl2-dev \
  python-gdal \
  libxml2-dev \
  libxslt-dev \
  libpq-dev

apt-get -q clean
