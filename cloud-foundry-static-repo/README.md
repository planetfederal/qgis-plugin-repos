# Cloud-Foundry Staticfile QGIS Plugin Repository 

This repository is completely static (no server-side code) and relies upon
the standard PCF Staticfile buildpack.

## Setup

The repository will serve throught http(s) whatever it finds in the `plugins`
directory, to setup a repository, you should follow the steps below:

1. copy into `plugins` directory all plugins that you wish to public in the repository
2. run the `update_index.py` script and pass `plugins` and your base URL as arguments, this will create the `plugins.xml` XML index file

Note: the **base URL** is the full URL to the directory
that will contain the plugins once deployed on PCF, the download URL will be
created by appending the zip file name to the base URL.

The following example command will copy all test plugins into the `plugins`
directory and create the `plugins.xml` index.

```
cp tests/data/*.zip plugins
./update_index.py plugins https://cloud-foundry-
static-repo.cfapps.io
```

## Deploy

You might want to review and adjust the `manifest.yml` file, in particular the
`disk_quota`, `name` and `domain`, to reflect your actual installation.

When done, simply run
```
cf push
```

## Testing

You can run unit tests for the index generation code with:
```
nosetests -s
```
