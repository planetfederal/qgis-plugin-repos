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


