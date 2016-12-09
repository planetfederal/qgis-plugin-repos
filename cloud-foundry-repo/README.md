# Cloud-Foundry QGIS Plugins Experimental Repository

This is an experimental repository that works on Cloud-Foundry, with the
following stack:

* redis
* Python Flask

There are two different applications: admin panel and server.

FIXME: there is some code duplication in the two directories, unfortunately
CF do not support symlinks.


## Plugin admin panel

Support plugin listing, deletion and upload.

https://plugins-admin.cfapps.io


TODO: metdata editing (API is already in place)

## Plugin XML server

Serves the plugins XML

https://plugins-server.cfapps.io

TODO: filtering and caching of the pre-filtered XMLs


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

Plugin server has some API tests.

TODO: web tests.

### Running the tests

```
cd plugins_admin
nosetests -s
```


## Running locally

```
cd plugins_admin
FLASK_DEBUG=1 python main.py
```


```
cd plugins_server
FLASK_DEBUG=1 python main.py
```
