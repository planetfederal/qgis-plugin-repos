#!/bin/bash

set -e

# Bug fix: https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1325142/comments/38
# dpkg-divert --local --add /etc/init.d/systemd-logind \
#  && ln -s /bin/true /etc/init.d/systemd-logind

# Avoid 'ERROR: invoke-rc.d: policy-rc.d denied execution'
# echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d

# Use apt-catcher-ng caching
if [ -n "${APT_CATCHER_IP}" ] && [ "${APT_CATCHER_IP}" != "None" ]; then
  echo 'Acquire::http { Proxy "http://'${APT_CATCHER_IP}':3142"; };' >> /etc/apt/apt.conf.d/01proxy
fi

# Specific versions
NGINX_VERSION=1.9.11-1~jessie

apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62
echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list

# add backports for OpenSSL 1.0.2+
echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list

apt-get -y update
apt-get -y upgrade
DEBIAN_FRONTEND=noninteractive apt-get -y install \
  nano \
  sudo \
  git \
  supervisor \
  ca-certificates \
  curl \
  gettext-base \
  openssh-server \
  python-pip \
  python-lxml \
  python-dev \
  vim

# backport of OpenSSL 1.0.2+ (instead of stable's 1.0.1)
DEBIAN_FRONTEND=noninteractive apt-get -y -t jessie-backports install "openssl"

# update nginx gpg key and install
curl https://nginx.org/keys/nginx_signing.key | apt-key add -
DEBIAN_FRONTEND=noninteractive apt-get -y install nginx=${NGINX_VERSION}

# Install certbot for letsencrypt certificates (used by 'dev' and 'beta' repos)
DEBIAN_FRONTEND=noninteractive apt-get -y install certbot -t jessie-backports

pip install uwsgi
apt-get -q clean
apt-get -q purge
rm -rf /var/lib/apt/lists/*

# NOTE: SSH user, whose uid all data containers should reference
adduser --system --ingroup users --shell /bin/bash --uid 106 ${SSH_USER}
echo "${SSH_USER}:${SSH_USER_PASS}" | chpasswd
su -c "gpasswd -a ${SSH_USER} sudo"
