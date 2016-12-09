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
from functools import wraps
from flask import Flask, request, make_response, Response
from flask import render_template
from flask_bootstrap import Bootstrap
from plugin import Plugin
from plugin_exceptions import DoesNotExist
from werkzeug.utils import secure_filename


# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 9099))

app = Flask(__name__)
Bootstrap(app)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == os.getenv("USERNAME", 'admin') and password == os.getenv("PASSWORD", 'password')

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
    return render_template('error.html', error=error)

@app.route('/')
@requires_auth
def plugins_list():
    message = None
    plugins = Plugin.all()
    if not len(plugins):
        message = 'There are no plugins.'
    return render_template('list.html',
                           title='Plugin list',
                           plugins=plugins,
                           message=message)


@app.route('/details/<key>')
@requires_auth
def plugin_details(key):
    message = None
    plugin = Plugin(key)
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
        except DoesNotExist:
            return render_error('{} does not exists'.format(key))
    else:
        try:
            plugin = Plugin(key)
            title = 'Confirm deletion of Plugin {} version {}?'.format(plugin.name, plugin.version)
            show_form = True
        except DoesNotExist:
            return render_error('{} does not exists'.format(key))

    return render_template('delete.html',
                           title=title,
                           plugin=plugin,
                           show_form=show_form,
                           message=message)


@app.route('/download/<key>')
@requires_auth
def plugin_download(key):
    try:
        plugin = Plugin(key)
        plugin.incr_downloads()
        response = make_response(plugin.blob)
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = \
            'inline; filename=%s.zip' % re.sub("[^A-z0-9]", '_', plugin.get_key())
        return response
    except DoesNotExist:
        return render_error('{} does not exists'.format(key))


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
                plugin = Plugin.create_from_zip(file)
                message = 'Plugin {} version {} created'.format(plugin.name, plugin.version)
            else:
                message = 'File does not have a zip extension'
    return render_template('upload.html', message=message)


@app.route('/plugins.xml')
@requires_auth
def plugins_xml():
    """Create the XML file"""
    plugins = Plugin.all()
    response = make_response(render_template('plugins.xml', plugins=plugins))
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'inline; plugins.xml'
    return response

@app.route('/plugins.xsl')
@requires_auth
def plugins_xsl():
    """Create the XML file"""
    return app.send_static_file('plugins.xsl')


if __name__ == '__main__':
    # Run the app, listening on all IPs with our chosen port number
    app.run(host='0.0.0.0', port=port)
