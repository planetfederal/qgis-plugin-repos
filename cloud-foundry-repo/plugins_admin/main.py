# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
The plugins admin application
Author: Alessandro Pasotti

"""
import os
import re
import base64
from functools import wraps
from flask import Flask, request, make_response, Response, abort, request
from flask import render_template
from flask_bootstrap import Bootstrap
from plugin import Plugin
from plugin_exceptions import DoesNotExist
from werkzeug.utils import secure_filename
from flask_restful import Resource, Api
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
Bootstrap(app)
api = Api(app)

if syslog_host is not None:
    logger = logging.getLogger("QGIS Plugin Repository Admin Panel")
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


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    is_valid = username == os.getenv("USERNAME", 'admin') and password == os.getenv("PASSWORD", 'password')
    if is_valid:
        log("User %s authenticated successfully" % username)
    else:
        log("Access denied for user %s" % username)
    return is_valid


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def render_error(error):
    log("View error: %s" % error)
    return render_template('error.html', error=error)

@app.route('/')
@requires_auth
def plugins_list():
    message = None
    plugins = Plugin.all()
    if not len(plugins):
        message = 'There are no plugins.'
    log("Plugins listed")
    return render_template('list.html',
                           title='Plugin list',
                           plugins=plugins,
                           message=message)


@app.route('/details/<key>')
@requires_auth
def plugin_details(key):
    message = None
    try:
        plugin = Plugin(key)
    except DoesNotExist:
        return render_error('<b>{}</b> does not exists'.format(key))
    log("Plugin details for %s" % key)
    return render_template('details.html',
                           title="{} - ver. {}".format(plugin.name, plugin.version),
                           plugin=plugin,
                           message=message)


@app.route('/delete/<key>', methods=['GET', 'POST'])
@requires_auth
def plugin_delete(key):
    message = None
    if request.method == 'POST':
        show_form = False
        try:
            plugin = Plugin(key)
            title = 'Plugin {} version {} deleted'.format(plugin.name, plugin.version)
            plugin.delete(key)
            log("Plugin %s has been deleted" % key)
        except DoesNotExist:
            return render_error('<b>{}</b> does not exists'.format(key))
    else:
        try:
            plugin = Plugin(key)
            title = 'Confirm deletion of Plugin {} version {}?'.format(plugin.name, plugin.version)
            show_form = True
            log("Plugin %s deletion confirmation asked" % key)
        except DoesNotExist:
            return render_error('{} does not exists'.format(key))

    return render_template('delete.html',
                           title=title,
                           plugin=plugin,
                           show_form=show_form,
                           message=message)


@app.route('/download/<key>/<package_name>.zip')
@requires_auth
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


@app.route('/upload', methods=['GET', 'POST'])
@requires_auth
def plugin_upload():
    message = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            message = 'No file part'
        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                message = 'No selected file'
            elif file and '.' in file.filename and \
                    file.filename.rsplit('.', 1)[1] == 'zip':
                file.filename = secure_filename(file.filename)
                # Create plugin
                plugin = Plugin.create_from_zip(file, file.filename)
                message = 'Plugin {} version {} created'.format(plugin.name, plugin.version)
            else:
                message = 'File does not have a zip extension'
    log("Plugin upload message: %s" % message)
    return render_template('upload.html', message=message)


@app.route('/plugins.xml')
@requires_auth
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
    return response

@app.route('/plugins.xsl')
@requires_auth
def plugins_xsl():
    """Create the XML file"""
    return app.send_static_file('plugins.xsl')


################################################################################
# REST API
#

class PluginMetadata(Resource):
    @requires_auth
    def get(self, key, metadata_key):
        try:
            plugin = Plugin(key)
        except DoesNotExist:
            abort(404)
        return {metadata_key: getattr(plugin, metadata_key) }

    @requires_auth
    def post(self, key, metadata_key):
        try:
            plugin = Plugin(key)
        except DoesNotExist:
            abort(404)

        metadata_value = request.data
        plugin.set_metadata(metadata_key, metadata_value)
        # Re-read
        plugin = Plugin(plugin.key)
        return {metadata_key: getattr(plugin, metadata_key) }

api.add_resource(PluginMetadata, '/rest/metadata/<string:key>/<string:metadata_key>')

class PluginPackage(Resource):
    @requires_auth
    def get(self, key):
        try:
            plugin = Plugin(key)
        except DoesNotExist:
            abort(404)
        return {key: base64.b64encode(plugin.blob)}

    @requires_auth
    def post(self):
        return {'result': 'success'}

    @requires_auth
    def delete(self, key):
        try:
            plugin = Plugin(key)
        except DoesNotExist:
            abort(404)
        plugin.delete(plugin.key)
        return {'result': 'success'}

api.add_resource(PluginPackage, '/rest/package/<string:key>')

class PluginList(Resource):
    @requires_auth
    def get(self):
        return {'plugins': {p.key: p.metadata for p in Plugin.all()}}

api.add_resource(PluginList, '/rest/plugins')



if __name__ == '__main__':
    # Run the app, listening on all IPs with our chosen port number
    app.run(host='0.0.0.0', port=port)
