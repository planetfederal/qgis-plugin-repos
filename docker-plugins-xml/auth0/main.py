# -*- coding: utf-8 -*-

"""
***************************************************************************
    This script is the entry point for the QGIS plugins repository.

    It handles the filtering on the plugins.xml file based on qgis version
    passed on the query string.

    Authentication is supported for the following route
     ``/plugins/packages-auth/<string:plugin>``

     The following autentication methods are supported:

     - HTTP Basic with username and password
     - Authorization Request Header Field access token (Bearer)
     - HTTP GET access token passed on the query string as `access_token`
     - HTTP POST Form-Encoded Body Parameter access token passed as
       `access_token`

    For installation and configuration instructions, please see `README.md`

    ---------------------
    Date                 : April 2016
    Copyright            : © 2016 Boundless
    Contact              : apasotti@boundlessgeo.com
    Author               : Alessandro Pasotti

***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Alessandro Pasotti'
__date__ = 'April 2016 '


import os
from lxml import etree
from functools import wraps

from flask import (
    Flask,
    request,
    Response,
    _request_ctx_stack,
    make_response,
    send_from_directory,
    abort,
)


from auth0.v2 import authentication, Auth0Error
from settings import client_id, client_domain

def vjust(str, level=3, delim='.', bitsize=3, fillchar=' ', force_zero=False):
    """
    Normalize a dotted version string.

    1.12 becomes : 1.    12
    1.1  becomes : 1.     1

    if force_zero=True and level=2:

    1.12 becomes : 1.    12.     0
    1.1  becomes : 1.     1.     0

    """
    if not str:
        return str
    nb = str.count(delim)
    if nb < level:
        if force_zero:
            str += (level-nb) * (delim+'0')
        else:
            str += (level-nb) * delim
    parts = []
    for v in str.split(delim)[:level+1]:
        if not v:
            parts.append(v.rjust(bitsize, '#'))
        else:
            parts.append(v.rjust(bitsize, fillchar))
    return delim.join(parts)

app = Flask(__name__)

def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def check_authentication(username, password):
    """
    This function is called to check if a username /
    password combination is valid.
    A login is performed and the access_token is set in the
    app context and will be available for other methods by accessing
    the request context.

    Returns True if credentials are valid, False in case of authentication
    errors.
    """
    # Login
    db_authentication = authentication.Database(client_domain)
    try:
        response = db_authentication.login(client_id, username, password, 'Username-Password-Authentication')
        access_token = response.get('access_token')
        if app.debug:
            app.logger.debug("Got access_token %s" % access_token)
        # Store
        _request_ctx_stack.top.current_user_token = access_token
        user_authentication = authentication.Users(client_domain)
        user_info = user_authentication.userinfo(access_token)
        if user_info is 'Unauthorized':
            raise Auth0Error(user_info)
    except Auth0Error, e:
        if app.debug:
            app.logger.debug("Auth0Error while authenticating user {0} {1}".format(username, e))
        return False
    return True


def handle_error(error, status_code):
    """
    Format error response and append status code.
    """
    if app.debug:
        app.logger.debug("Token error: {0} {1}".format(error.get('description'), status_code))
    return False


def authorize(access_token):
    """
    This function retrieves user information based on a valid token,
    if the token is expired or not valid, the function return False
    Other checks for user authorization on a particular asset should be
    implemented here
    """
    user_authentication = authentication.Users(client_domain)
    user_info = user_authentication.userinfo(access_token)
    if user_info == 'Unauthorized':
        return False
    # Place other checks here
    return True


def requires_auth(f):
    """
    Requires valid HTTP basic credentials or a token and checks
    them against  Auth0 endpoint.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = None
        # Check HTTP basic auth, set access_token if authenticated
        auth = request.authorization
        if auth is not None and not check_authentication(auth.username, auth.password):
            return authenticate()
        # Try to get access_token token from  various sources
        # Token in the headers
        try:
            k, v = request.headers.get('Authorization').split(' ')
            if k.lower() == 'bearer':
                access_token = v
        except (ValueError, AttributeError, KeyError):
            pass
        # Token was set by check_authentication
        try:
            access_token = _request_ctx_stack.top.current_user_token
        except AttributeError:
            pass
        # Plain HTTP GET and POST
        if access_token is None and request.method == 'GET':
            access_token = request.args.get('access_token', access_token)
        if request.method == 'POST':
            try:
                access_token = request.form['access_token']
            except KeyError:
                pass
        # No valid token provided or the token is present but it is not valid
        # or other rules deny access to the requested resource
        if access_token is None or not authorize(access_token):
            return authenticate()
        # Set for debug
        _request_ctx_stack.top.current_user_token = access_token
        return f(*args, **kwargs)
    return decorated


@app.route("/plugins.xml")
@app.route("/plugins/plugins.xml")
def filter_xml():
    """
    Filters plugins.xml removing incompatible plugins.
    If no qgis parameter is found in the query string,
    the whole plugins.xml file is served as is.
    """
    # Points to the real file, not the symlink
    xml_dir = os.path.join(request.environ.get('DOCUMENT_ROOT', ''), 'plugins')
    if not request.query_string:
        return send_from_directory(xml_dir, 'plugins.xml')
    elif request.args.get('qgis') is None:
        abort(404)
    else:
        try:
            xml = etree.parse(os.path.join(xml_dir, 'plugins.xml'))
        except IOError:
            return make_response("Cannot find plugins.xml", 404)
        qgis_version = vjust(request.args.get('qgis'), force_zero=True)
        for e in xml.xpath('//pyqgis_plugin'):
            if not (vjust(e.find('qgis_minimum_version').text, force_zero=True)
                    <= qgis_version and qgis_version
                    <= vjust(e.find('qgis_maximum_version').text, force_zero=True)):
                e.getparent().remove(e)
        response = make_response(etree.tostring(xml, pretty_print=app.debug,
                                                xml_declaration=True))
        response.headers['Content-type'] = 'text/xml'
        return response


@app.route("/plugins/packages-auth/<string:plugin_name>", methods=['GET', 'POST'])
@requires_auth
def securedPlugins(plugin_name):
    """
    Downloads a secured plugin.

    Also passes the access token back into a custom 'X-Access-Token'
    header.
    The caller can re-use the token for future calls.
    """
    if app.debug:
        app.logger.debug("Downloading plugin {0} with token {1}".format(plugin_name, _request_ctx_stack.top.current_user_token))
    plugins_dir = os.path.join(request.environ.get('DOCUMENT_ROOT', ''), 'plugins', 'packages-auth')
    plugin_path = os.path.join(plugins_dir, plugin_name)
    try:
        the_plugin = open(plugin_path, 'r')
        response = make_response(the_plugin.read())
        response.headers['Content-type'] = 'application/zip'
        response.headers['Content-Disposition'] = "attachment; filename=%s" % plugin_name
        response.headers['X-Access-Token'] = _request_ctx_stack.top.current_user_token
        the_plugin.close()
    except IOError:
        abort(404)
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8000)
