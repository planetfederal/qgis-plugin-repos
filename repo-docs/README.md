# Boundless QGIS Plugin Repository HTML

Generate HTML documentation for Boundless QGIS plugin repository.

## Generation

Run the following in a terminal (you will need to have [pip][pip] installed, and
_may_ need to prefix the command with `sudo` depending upon your Python):

    $> pip install -r requirements.txt

Once the required Sphinx package is installed, build the docs (this requires
`sphinx-build` to be on your PATH):

    $> sphinx-build -b html source build

Docs will be generated and output to the **build** directory.

[pip]: https://pypi.python.org/pypi/pip

## Themes git submodule

This repository uses external repositories as submodules for documentation themes. Therefore in order to include the external repositories during cloning you should use the *--recursive* option:

``git clone --recursive http://github.com/boundlessgeo/qgis-connect-plugin.git``

If you have clone it already without the *--recursive* option you can do:

``git submodule init``
``git submodule update``

Also, to update the submodules whenever there are changes in the remote repositories one should do:

``git submodule update --remote``
