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


# Add security updates to sources.list
echo "deb http://security.debian.org/debian-security stretch/updates main contrib non-free" >> /etc/apt/sources.list

apt-get -y update
apt-get -y upgrade
DEBIAN_FRONTEND=noninteractive apt-get -y install \
  nano \
  sudo \
  cron \
  unattended-upgrades \
  git \
  gnupg \
  supervisor \
  ca-certificates \
  curl \
  gettext-base \
  openssh-server \
  python-pip \
  python-lxml \
  python-dev \
  vim \
  certbot
# certbot for letsencrypt certificates (used by 'dev' and 'beta' repos)

# Nginx from project's repo
NGINX_VERSION=1.12.0-1~stretch

# Update nginx gpg key and install
curl https://nginx.org/keys/nginx_signing.key | apt-key add -
echo "deb http://nginx.org/packages/debian/ stretch nginx" >> /etc/apt/sources.list
apt-get -y update

DEBIAN_FRONTEND=noninteractive apt-get -y install nginx=${NGINX_VERSION}

# WSGI
pip install uwsgi

# Clean up image
apt-get -q clean
apt-get -q purge
rm -rf /var/lib/apt/lists/*

# NOTE: SSH user, whose uid all data containers should reference
adduser --system --ingroup users --shell /bin/bash --uid 110 ${SSH_USER}
echo "${SSH_USER}:${SSH_USER_PASS}" | chpasswd
su -c "gpasswd -a ${SSH_USER} sudo"
