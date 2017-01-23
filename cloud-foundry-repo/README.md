# Cloud-Foundry QGIS Plugins Repository

This is a QGIS Plugin repository that works on Cloud-Foundry, with the
following stack:

* redis
* Python Flask

There are two different applications: _admin panel_ and _plugin server_.

## Plugin server

Provides an XML listing of the available plugins and a way to download
them. The plugin server is read-only and does not provide any way to
update the available plugins.

## Admin panel

Provides a web GUI and a REST API for uploading, deleting and updating
the plugin repository. This application does not need to be alway on
and the server application is all yo need to serve and deliver the plugins
to the users.

## Prerequisites

A redis cloud service instance from the Pivotal Web Services marketplace named `myredis` (or set a different name in the  `manifest.yml` file)

## Plugin admin panel

Support plugin listing, deletion and upload.

https://plugins-admin.cfapps.io


## Plugin XML server

Serves the plugins XML

https://plugins-server.cfapps.io/plugins.xml


## Configuration

All configuration is done through environment variables.

All applications:
* PORT: the port for the development server when running locally
* SYSLOG_HOST: _optional_ host for the syslog logging, default to `None` (logging disabled, set to the IP address of the syslog server to activate logging)
* SYSLOG_PORT: _optional_ port for the syslog logging, default to 514
* SYSLOG_FACILITY:  _optional_ facility integer code for the syslog logging, default to 1 (`SysLogHandler.LOG_USER`)
* SYSLOG_FORMATTER: _optional_ formatting string in Python logging syntax, default to `[%(asctime)s] %(levelname)s %(process)d [%(name)s] - %(message)s`

`settings.py` contains some global metadata settings for the validator, that
usually do not need to be changed.

Admin application:
* USERNAME: authentication for the admin panel
* PASSWORD: authentication for the admin panel


## Testing

Plugin server has a comprehensive API test coverage.

TODO: test for the web GUI.

### Running the tests

```
cd plugins_admin
nosetests -s
```

## REST API

A REST API is available in the admin application:

**key** is composed by `Plugin:<plugin_name>:<plugin_version>`

+ `/rest/metadata/<string:key>/<string:metadata_key>` GET or POST a metadata
+ `/rest/package/<string:key>` GET or POST a plugins zip file, or DELETE a plugin
+ `/rest/plugins` GET all plugins as a keys and metadata hash


## Running locally

```
cd plugins_admin
FLASK_DEBUG=1 python main.py
```


```
cd plugins_server
FLASK_DEBUG=1 python main.py
```


# Deploying on PCF

A convenience deploy `deploy.sh` script that accepts two optional parameters for
username and password is provided:

```
./deploy.sh user secret
```

To get full control over the applications configuration (e.g. to congigure
syslog logging) you can directly edit the `manifest.yml` file.
