FROM busybox
MAINTAINER Larry Shaffer<lshaffer@boundlessgeo.com>

ARG SSH_USER=user
ARG UPLOADED_BY=Boundless
ARG DOMAIN_TLD=qgis.boundless.test
ARG DOMAIN_TLD_BETA=qgis-beta.boundless.test
ARG DOMAIN_TLD_DEV=qgis-dev.boundless.test
ARG DOMAIN_TLD_MIRROR=qgis-mirror.boundless.test

ADD setup.sh /tmp/
RUN sh /tmp/setup.sh

ADD resources /opt/setup/
RUN sh /opt/setup/setup-repo.sh

USER ${SSH_USER}
VOLUME /var/www /opt/repo-updater
CMD ["echo", "WWW data and updater script container for QGIS plugin repo"]
