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
import re
from flask import Flask, make_response
from flask import render_template
from plugin import Plugin
from plugin_exceptions import DoesNotExist


# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 9099))

app = Flask(__name__)


@app.route('/')
@app.route('/plugins.xml')
def plugins_xml():
    """Create the XML file"""
    plugins = Plugin.all()
    response = make_response(render_template('plugins.xml', plugins=plugins))
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'inline; plugins.xml'
    return response


@app.route('/download/<key>')
def plugin_download(key):
    try:
        plugin = Plugin(key)
        plugin.incr_downloads()
        response = make_response(plugin.blob)
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = \
            'inline; filename=%s.zip' % re.sub("[^A-z0-9]", '_', plugin.key)
        return response
    except DoesNotExist:
        return render_error('<b>{}</b> does not exists'.format(key))


@app.route('/plugins.xsl')
def plugins_xsl():
    """Create the XML file"""
    return app.send_static_file('plugins.xsl')


if __name__ == '__main__':
    # Run the app, listening on all IPs with our chosen port number
    app.run(host='0.0.0.0', port=port)
