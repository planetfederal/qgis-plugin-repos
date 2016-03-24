FROM ubuntu:latest
MAINTAINER Larry Shaffer<lshaffer@boundlessgeo.com>

ARG APT_CATCHER_IP=localhost

ADD setup.sh /tmp/
RUN chmod 0700 /tmp/setup.sh && sh /tmp/setup.sh

ADD resources/app-requirements.sh /opt/
RUN chmod 0700 /opt/app-requirements.sh && bash /opt/app-requirements.sh

ADD resources/app-setup.sh resources/settings_local.py /opt/
RUN chmod 0700 /opt/app-setup.sh && bash /opt/app-setup.sh

WORKDIR /opt/QGIS-Django/qgis-app
EXPOSE 8000
CMD . /opt/QGIS-Django/venv/bin/activate;\
  python manage.py runserver;
#CMD ["python", "manage.py", "runserver"]
