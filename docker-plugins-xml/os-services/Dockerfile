FROM debian:stretch
MAINTAINER Larry Shaffer<lshaffer@boundlessgeo.com>

ARG SSH_USER=user
ARG SSH_USER_PASS=pass
ARG APT_CATCHER_IP=''

ADD setup.sh /tmp/
RUN bash /tmp/setup.sh

ADD resources /opt/setup/
RUN bash /opt/setup/setup-services.sh

# Add user and group for uwsgi
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

# Fix for nano
ENV TERM xterm

EXPOSE 80 443 2222
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
