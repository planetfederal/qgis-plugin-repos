#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2017 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
Create an XML index (plugins.xml) from a directory of QGIS plugins zip files.
Author: Alessandro Pasotti

Slightly inspired from http://reinout.vanrees.org/weblog/2016/08/29/qgis-plugin-repo.html
"""
import os
import sys
import zipfile
import argparse
try: # Py2
    from ConfigParser import ConfigParser, NoOptionError
except ImportError: # Py3
    from configparser import ConfigParser, NoOptionError

START = '''<?xml version="1.0" encoding="UTF-8" ?>
<?xml-stylesheet type="text/xsl" href="plugins.xsl" ?>
<plugins>
'''

END = '''
</plugins>
'''

TEMPLATE = '''
<pyqgis_plugin name="{name}" version="{version}">
    <description><![CDATA[{description}]]></description>
    <about><![CDATA[{about}]]></about>
    <version>{version}</version>
    <qgis_minimum_version>{qgis_minimum_version}</qgis_minimum_version>
    <qgis_maximum_version>{qgis_maximum_version}</qgis_maximum_version>
    <homepage>{homepage}</homepage>
    <file_name>{filename}</file_name>
    <icon>icons/opengeo/0.8.0-201609211649-1d16dfb.png</icon>
    <author_name><![CDATA[{author_name}]]></author_name>
    <download_url>{download_url}</download_url>
    <experimental>{experimental}</experimental>
    <deprecated>{deprecated}</deprecated>
    <tracker><![CDATA[{tracker}]]></tracker>
    <repository><![CDATA[{repository}]]></repository>
    <changelog><![CDATA[{changelog}]]></changelog>
    <tags>{tags}</tags>
  </pyqgis_plugin>
'''

PLUGINS_XML = 'plugins.xml'


class PluginZipFile(object):
    """Wrapper around a zip file that extracts metadata"""

    def __init__(self, filename, base_url):
        self.filename = filename
        self.base_url = base_url

    def extract_metadata(self):
        """Return info from the metadata.txt inside the zip file"""
        opened_zip_file = zipfile.ZipFile(self.filename, 'r')
        expected = [f.filename for f in opened_zip_file.filelist if f.filename.endswith('metadata.txt')][0]
        metadata = ConfigParser()
        try: # Py2
            metadata.readfp(opened_zip_file.open(expected))
        except TypeError: # Py3
            md = opened_zip_file.open(expected).read()
            metadata.read_string(md.decode('utf-8'))

        result = {}

        def get_option(section, option, default=''):
            try:
                return metadata.get(section, option)
            except NoOptionError:
                return default

        result['name'] = get_option('general', 'name')
        result['about'] = get_option('general', 'about')
        result['download_url'] = get_option('general', 'about')
        result['version'] = get_option('general', 'version')
        result['description'] = get_option('general', 'description')
        result['qgis_minimum_version'] = get_option('general', 'qgisMinimumVersion')
        result['qgis_maximum_version'] = get_option('general', 'qgisMaximumVersion', '')
        result['author_name'] = get_option('general', 'author').replace('&', '&amp;')
        result['homepage'] = get_option('general', 'homepage', '')
        result['tracker'] = get_option('general', 'tracker', '')
        result['repository'] = get_option('general', 'repository', '')
        result['tags'] = get_option('general', 'tags', '')
        result['changelog'] = get_option('general', 'changelog')
        result['experimental'] = get_option('general', 'experimental', False)
        result['deprecated'] = get_option('general', 'experimental', False)
        return result

    def as_xml(self):
        """Return info about zip file as xml"""
        metadata = self.extract_metadata()
        metadata['filename'] = os.path.basename(self.filename)
        metadata['download_url'] = self.base_url + os.path.basename(self.filename)
        return TEMPLATE.format(**metadata)

def abort(msg):
    print(msg)
    sys.exit(1)


def process(directory, base_url, verbose):
    zip_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith('.zip')]

    if verbose:
        print("%s zip files found in directory %s" % (len(zip_files), directory))

    if not base_url.endswith('/'):
        base_url = base_url + '/'

    plugin_metadata = []
    for filename in zip_files:
        if verbose:
            print("Processing %s ..." % filename)
        plugin_metadata.append(PluginZipFile(filename, base_url))


    output = ''
    output += START
    for plugin_zip_file in plugin_metadata:
        try:
            output += plugin_zip_file.as_xml()
            if verbose:
                print("Writing metadata for plugin %s" % plugin_zip_file.filename)
        except Exception as e:
            print("Something went wrong with %s" % plugin_zip_file.filename)
            print(e)
    output += END
    plugins_xml_path = os.path.join(directory, PLUGINS_XML)
    open(plugins_xml_path, 'w').write(output)
    if verbose:
        print("Wrote %s" % plugins_xml_path)


def main():

    parser = argparse.ArgumentParser(description='Process the QGIS Plugin zipfiles in a given directory and creates an plugins.xml in the same folder')
    parser.add_argument('directory', default='.',
                    help='path to the directory that contains the plugin zipfiles')
    parser.add_argument('base_url',
                    help='base URL to the directory that contains the zipfiles, '
                         'this will be used as a prefix to build the download url '
                         'for the plugins')
    parser.add_argument('-v', '--verbose', action='store_true',
                    help='print detailed information on the stdout stream')


    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        abort("%s is not a valid directory" % args.directory)

    process(args.directory, args.base_url, args.verbose)
    sys.exit(0)


if __name__ == '__main__':
    main()
