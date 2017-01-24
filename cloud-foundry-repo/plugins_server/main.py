# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
Serve plugins.xml
Author: Alessandro Pasotti
"""
import os
from flask import Flask, make_response, request
from flask import render_template
from plugin import Plugin
from plugin_exceptions import DoesNotExist, ValidationError
import logging
from logging.handlers import SysLogHandler


# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 9099))
# Syslog
syslog_port = int(os.getenv("SYSLOG_PORT", 514))
syslog_host = os.getenv("SYSLOG_HOST")
syslog_facility = int(os.getenv("SYSLOG_FACILITY", SysLogHandler.LOG_USER))
syslog_formatter = os.getenv('SYSLOG_FORMATTER', '[%(asctime)s] %(levelname)s %(process)d [%(name)s] - %(message)s')

app = Flask(__name__)


if syslog_host is not None:
    logger = logging.getLogger("QGIS Plugin Repository Server")
    formatter = syslog_formatter
    logger.setLevel(logging.INFO)
    handler = SysLogHandler(address=(syslog_host, syslog_port),
                            facility=syslog_facility)
    handler.setFormatter(logging.Formatter(syslog_formatter))
    logger.addHandler(handler)
    logger.info("Initialised")
else:
    logger = None


def log(msg, level=logging.INFO):
    """Send a message to the logs"""
    if syslog_host is not None:
        logger.log(level, msg)


def render_error(error):
    log("View error: %s" % error)
    return render_template('error.html', error=error)


@app.route('/')
@app.route('/plugins.xml')
def plugins_xml():
    """Create the XML file"""
    version = None
    try:
        version = request.args.get('qgis')
    except KeyError:
        pass
    plugins = Plugin.all(version=version)
    response = make_response(render_template('plugins.xml', plugins=plugins))
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'inline; plugins.xml'
    log("XML requested for version: %s" % version)
    return response


@app.route('/download/<key>/<package_name>.zip')
def plugin_download(key, package_name):
    try:
        plugin = Plugin(key)
        plugin.incr_downloads()
        response = make_response(plugin.blob)
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = \
            'inline; filename=%s.zip' % package_name
        log("Plugin %s downloaded" % key)
        return response
    except DoesNotExist:
        return render_error('<b>{}</b> does not exists'.format(key))


@app.route('/plugins.xsl')
def plugins_xsl():
    """Create the XML file"""
    return app.send_static_file('plugins.xsl')


def app_bootstrap():
    """Load all zipfile plugins from the zipfiles folder"""
    zipfolder = os.path.join(os.path.dirname(__file__), 'zipfiles')
    if os.path.isdir(zipfolder):
        for path in [f for f in os.listdir(zipfolder)
                     if (os.path.isfile(os.path.join(zipfolder, f))
                     and f.endswith('.zip'))]:
            try:
                plugin = Plugin.create_from_zip(open(os.path.join(zipfolder, path)))
                log("Plugin: %s has been succesfully loaded" % plugin.key)
            except ValidationError as e:
                log("Plugin file: %s could not be loaded: %s" % (path, e))


if __name__ == '__main__':
    # Run the app, listening on all IPs with our chosen port number
    app_bootstrap()
    app.run(host='0.0.0.0', port=port)
