# Cloud-Foundry QGIS Plugins Repository

This is a QGIS Plugin repository that works on Cloud-Foundry, with the
following stack:

* redis
* Python Flask

There are two different applications: admin panel and server.


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

There is a `deploy.sh` script that accepts two optional parameters for
username and password:

```
./deploy.sh user secret
```
