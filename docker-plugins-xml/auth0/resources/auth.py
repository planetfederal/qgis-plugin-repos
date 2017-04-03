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

# Configuration:
CACHE_TIMEOUT = 60
from werkzeug.contrib.cache import SimpleCache as AuthCache
profiles_cache = AuthCache()
roles_cache = AuthCache()
# End configuration

import os
from lxml import etree
from functools import wraps
import json
import time
import jwt
import base64

from flask import (
    request,
    Response,
    _request_ctx_stack,
    make_response,
    abort,
)


from auth0.v2 import authentication, Auth0Error
import settings
from main import app
app.debug = settings.debug


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


@app.errorhandler(403)
def custom_403(error):
    return Response('Forbidden - user role is not authorized', 403)

def message_log(msg):
    if app.debug:
        app.logger.debug(msg)

def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def get_user_profile(access_token):
    """
    Return and caches the user Profile from user access_token.
    First check for cached values.
    """
    message_log("Retrieving user profile for token %s" % access_token)
    user_profile = profiles_cache.get(access_token)
    if user_profile is not None:
        message_log("Using cached user profile for token %s" % access_token)
    else:
        message_log("Fetching user profile for token %s" % access_token)
        user_authentication = authentication.Users(settings.client_domain)
        # Throttle
        for i in range(1, 4):
            user_profile = user_authentication.userinfo(access_token)
            if user_profile == 'Too Many Requests':
                message_log("Too many requests: throttling (%s seconds) for token %s" % (i*2, access_token))
                time.sleep(i*2)
            else:
                break
        if user_profile == 'Unauthorized':
            raise Auth0Error(user_profile)
        try:
            user_profile = json.loads(user_profile)
            profiles_cache.set(access_token, user_profile, timeout=CACHE_TIMEOUT)
        except ValueError:
            message_log("Returning empty user profile")
            return False
    message_log("Returning user profile %s" % user_profile)
    return user_profile


def get_user_roles(access_token):
    """
    Return the user Desktop roles set from user access_token.
    """
    user_roles = roles_cache.get(access_token)
    if user_roles:
        return set(user_roles)
    user_profile = get_user_profile(access_token)
    if not user_profile:
        return set()
    user_info_j = user_profile.get("SiteRole")
    user_roles = user_info_j.split(',')
    roles_cache.set(access_token, user_roles, timeout=CACHE_TIMEOUT)
    # Always cast to set
    message_log("Returning user role %s" % user_roles)
    return set(user_roles)


def get_plugin_roles(plugin_name):
    """
    Retrieve the plugin roles from the xml
    """
    # Default
    plugin_roles = set()
    # Load xml from current folder
    # Points to the real file, not the symlink
    xml_dir = os.path.join(request.environ.get('DOCUMENT_ROOT', ''), 'plugins')
    tree = etree.parse(os.path.join(xml_dir, 'plugins.xml'))
    try:
        plugin_element = tree.xpath('//file_name[text()="%s"]' % plugin_name)[0]
        role_name = plugin_element.getparent().find('authorization_role').text
        plugin_roles = set(role_name.split(','))
    except IndexError:
        message_log("Cannot find %s in plugins.xml" % plugin_name)
    except AttributeError, e:
        message_log("Cannot find %s role in plugins.xml (%s)" % (plugin_name, e))
    except ValueError, e:
        message_log("Cannot find index for role in plugin %s (%s)" % (plugin_name, e))
    return plugin_roles


def check_authentication(username, password):
    """
    This function is called to check if a username /
    password combination is valid.
    A login is performed and the access_token is set in the
    app context and will be available for other methods by accessing
    the request context.
    The user role is also retrieved and stored in the roles cache ready
    for use in the authorization function.
    Returns True if credentials are valid, False in case of authentication
    errors.
    """
    # Login
    db_authentication = authentication.Database(settings.client_domain)
    try:
        response = db_authentication.login(settings.client_id,
                                           username, password,
                                           'Username-Password-Authentication',
                                           scope='openid SiteRole')
        access_token = response.get('access_token')
        # Get the JWT token (optionally used if secret is specified)
        if settings.client_secret is not None:
            try:
                id_token = response.get('id_token')
                payload = jwt.decode(
                    id_token,
                    base64.b64decode(settings.client_secret.replace("_","/").replace("-","+")),
                    audience=settings.client_id
                )
                message_log("Got payload %s from JWT: %s" % (payload, id_token))
                user_roles = payload.get('SiteRole', '').split(',')
                message_log("Got access_token %s and user roles %s for user %s" % (access_token, user_roles, username))
                # Store user roles for authorization
                roles_cache.set(access_token, user_roles, timeout=CACHE_TIMEOUT)
            except jwt.exceptions.DecodeError, e:
                message_log("%s for %s" % (e, access_token))
            except Exception, e:
                message_log("Wrong JWT decoding (%s) for %s" % (e, access_token))
        message_log("Got access_token %s" % access_token)
        # Store token
        _request_ctx_stack.top.current_user_token = access_token
        user_roles = get_user_roles(access_token)
        message_log("Auth0 successful authentication for user %s with role: %s" % (username, user_roles))
    except Auth0Error, e:
        message_log("Auth0Error while authenticating user %s %s" % (username, e))
        return False
    return True

def authorize(user_roles, plugin_roles):
    """
    The download is authorized if the plugin roles set is empty (the plugin does
    not require any particular role to be downloaded) or if the plugin roles and
    the user roles intersection is not empty.
    """
    if not plugin_roles:
        return True
    message_log("Comparing user roles  %s with plugin roles %s" % (user_roles, plugin_roles))
    return user_roles.intersection(plugin_roles)


def requires_auth(f):
    """
    Requires valid HTTP basic credentials or a token and checks
    them against Auth0 endpoint.
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
        # Plain old HTTP GET and POST
        if access_token is None and request.method == 'GET':
            access_token = request.args.get('access_token', access_token)
        if request.method == 'POST':
            try:
                access_token = request.form['access_token']
            except KeyError:
                pass
        # No valid token provided or the token is present but it is not valid
        # or other rules deny access to the requested resource
        if access_token is None:
            return authenticate()

        # If it's a plugin download:
        if 'plugin_name' in kwargs:
            plugin_roles = get_plugin_roles(kwargs.get('plugin_name'))
            message_log("Got plugin roles: %s" % plugin_roles)
            try:
                user_roles = get_user_roles(access_token)
                message_log("Got user roles: %s" % user_roles)
            except Auth0Error, e:
                message_log("Auth0Error: Forbidden - Returning 403: %s" % e)
                return abort(403)
            if not authorize(user_roles, plugin_roles):
                message_log("Forbidden - Returning 403")
                return abort(403)

        _request_ctx_stack.top.current_user_token = access_token
        message_log("Returning from requires_auth decorator")
        return f(*args, **kwargs)
    return decorated

@app.route("/api/user_profile", methods=['GET', 'POST'])
@requires_auth
def user_profile():
    """
    Return the user profile in JSON format.
    """
    access_token = _request_ctx_stack.top.current_user_token
    message_log("Got access token for user profile")
    user_profile = get_user_profile(access_token)
    user_profile['access_token'] = access_token
    return json.dumps(user_profile)



@app.route("/api/user_roles", methods=['GET', 'POST'])
@requires_auth
def user_roles():
    """
    Return the user roles in JSON format.
    """
    access_token = _request_ctx_stack.top.current_user_token
    message_log("Got access token for user roles")
    user_roles = get_user_roles(access_token)
    return json.dumps(list(user_roles))


@app.route("/plugins/packages-auth/<string:plugin_name>", methods=['GET', 'POST'])
@requires_auth
def securedPlugins(plugin_name):
    """
    Downloads a secured plugin.

    Also passes the access token back into a custom 'X-Access-Token'
    header.
    The caller can re-use the token for future calls.
    """
    message_log("Downloading plugin {0} with token {1}".format(plugin_name, _request_ctx_stack.top.current_user_token))
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
