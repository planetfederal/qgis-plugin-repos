
# Auth0 setup for plugin repos


The modifications provided in this directory, enable **Auth0** authentication
and *Desktop tiers* authorization for the plugins in the protected folder
(`packages-auth`).

Please refer to the [README for the main Docker repository][mdr] in the
parent directory of this repository for the full documentation.
The present document contains a description of the additional features
and methods available in **Auth0-enabled** repositories.

Supported authentication methods are:

- HTTP Basic with username and password
- Authorization Request Header Field access token (Bearer)
- HTTP GET access token passed on the query string as `access_token`
- HTTP POST Form-Encoded Body Parameter access token passed as
  `access_token`

[mdr]: https://github.com/boundlessgeo/qgis-plugin-repos/tree/master/docker-plugins-xml

## Building and running

To build, run and test the **Auth0-enabled** repository you can use the
versions of the `test-*.sh` scripts in the same directory of the current
`README.md` (`auth0`).

## Configuration

**Auth0** credentials are stored in `settings.py` (the default implementation
reads the values from an `.env` file).

You can either provide a `.env` file, fill in the correct credentials and store
it in the container as `/var/www/.env` or directly edit the `settings.py` file.

The client secret is not mandatory but it is recommended because it reduces
the number of calls to the Auth0 API endpoint by decoding signed JWT tokens.

A typical `.env` file looks like this:
```bash
AUTH0_CLIENT_ID=your_client_id
AUTH0_DOMAIN=your_domain.auth0.com
# Not mandatory but recommended:
#AUTH0_CLIENT_SECRET=*******************************
# Activate for debug (not for production!):
#DEBUG=True
```

### Caching of user roles

User roles are cached to avoid `Too many requests` HTTP responses from Auth0
endpoint while executing the tests.

The cache backend and duration can be set at the top of `main.py` (see comments
in the file).

### Debugging

To activate debug output from the server, set `DEBUG=True` in the `.env` file.

If you also want to see the Python stack trace from uwsgi, add
`--catch-exceptions` in `/etc/supervisor/conf.d/services.conf`:

    [program:app-uwsgi]
    ; --catch-exceptions for debugging only!
    command = /usr/local/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini --uid uwsgi --gid uwsgi --catch-exceptions

## Plugin Repository Updating/Editing

See the [README for the Python updater script][rus] in the **qgis-plugins-xml**
code repository for the base manual.

[rus]: https://github.com/boundlessgeo/qgis-plugins-xml

**Auth0** enabled repository accepts and extra string parameter `--role` that sets
the minimum Auth0 role that will be able to download the plugin, for example::

    $> scp uploads/test_plugin_1.zip boundless.test:/opt/repo-updater/uploads/

Run remote updater script on uploaded archive and set minimum role required for
download to `DesktopBasic`:

    $> ssh boundless.test "/opt/repo-updater/plugins-xml/plugins-xml.sh update --role DesktopBasic test_plugin_1.zip"


## Installation


An `install.sh` script is available in the `auth0` folder. The `install.sh`
script performs the installation of Auth0 enabled repository.


## Testing the endpoints

Please refer to the [base manual][mdr] in the top-level folder for detailed
instructions about building the dockers and upload example plugins.

### Fully automated tests

The directory `tests` contains a python test script that can be used
to test the dockerized repository created with `test-build.run load`
as explained in the [base manual][mdr].
The list of Python requirements for the test script can be found in the file
`resources/REQUIREMENTS.txt`.

Start the tests from the command line with:

    $> python endpoint_tests.py

The test uses three real test accounts that must be configured in `.env`:

    QGIS_FREE_USERNAME=********* # with Registered permissions
    QGIS_FREE_PASSWORD=*********
    QGIS_BASIC_USERNAME=******** # with DesktopBasic and Suite permissions
    QGIS_BASIC_PASSWORD=********
    QGIS_ENTERPRISE_USERNAME=*** # with DesktopEnterprise and Suite permissions
    QGIS_ENTERPRISE_PASSWORD=***


### Manual tests

The following endpoint is protected:
https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip

### Testing **GET** method with no credentials:

```bash
wget -S --no-check-certificate -O /dev/null 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 401 UNAUTHORIZED
Server: nginx
Date: Wed, 27 Apr 2016 14:09:54 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 90
Connection: keep-alive
WWW-Authenticate: Basic realm="Login Required"
```

### Testing **GET** method with valid credentials

Insert your username and password, if the username contains `@`, encode as `%40`:

```bash
wget -S --no-check-certificate -O /dev/null 'https://your_username%40your_domain.com:your_password@qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```

`XXXXXXXXXXXXX` is your access token that can be used to test the `access_token`
authentication.


### Testing **GET** method with invalid **access_token**:

```bash
wget -S --no-check-certificate -O /dev/null 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip?access_token=wrong_token_here'
HTTP/1.1 401 UNAUTHORIZED
Server: nginx
Date: Wed, 27 Apr 2016 14:20:11 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 90
Connection: keep-alive
WWW-Authenticate: Basic realm="Login Required"
```

### Testing **GET** method with valid **access_token**

Replace `XXXXXXXXXXXXX` with your valid `access_token`

```bash
wget -S --no-check-certificate -O /dev/null 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip?access_token=XXXXXXXXXXXXX'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```


### Testing Authorization Request Header Field access token (Bearer) method with wrong **access_token**

```bash
wget -S --no-check-certificate -O /dev/null --header="Authorization: Bearer wrong_token_here"  'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 401 UNAUTHORIZED
Server: nginx
Date: Wed, 27 Apr 2016 14:20:11 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 90
Connection: keep-alive
WWW-Authenticate: Basic realm="Login Required"
```


### Testing Authorization Request Header Field access token (Bearer) method with valid **access_token**

Replace `XXXXXXXXXXXXX` with your valid `access_token`

```bash
wget -S --no-check-certificate -O /dev/null --header="Authorization: Bearer XXXXXXXXXXXXX"  'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```

### Testing **POST** method with wrong access_token:

```bash
wget -S --no-check-certificate -O /dev/nul l--post-data="access_token=wrong_token_here" 'https://qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
  HTTP/1.1 401 UNAUTHORIZED
  Server: nginx
  Date: Wed, 27 Apr 2016 14:09:54 GMT
  Content-Type: text/html; charset=utf-8
  Content-Length: 90
  Connection: keep-alive
  WWW-Authenticate: Basic realm="Login Required"
```

### Testing **POST** method with valid access_token

Replace `XXXXXXXXXXXXX` with your valid `access_token`

```bash
wget -S --no-check-certificate -O /dev/null --post-data="access_token=XXXXXXXXXXXXX" 'https:/qgis.boundless.test/plugins/packages-auth/test_plugin_3.0.1.zip'
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 27 Apr 2016 14:12:07 GMT
Content-Type: application/zip
Content-Length: 5082
Connection: keep-alive
Content-Disposition: attachment; filename=test_plugin_3.0.1.zip
X-Access-Token: XXXXXXXXXXXXX
```
