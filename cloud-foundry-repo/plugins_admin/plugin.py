# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
The plugins model
Author: Alessandro Pasotti

"""
from flask import Flask
import ConfigParser
import codecs
import zipfile
from connection import db
from plugin_exceptions import *
from version_compare import isCompatible
from cStringIO import StringIO
from validator import validator

# Derived metadata, not to be stored in the zipfile metadata.txt
EXCLUDE_METADATA=('metadata_source', 'icon_content')

class Plugin:

    @classmethod
    def make_key(cls, name, version):
        return 'Plugin:{}:{}'.format(name, version)

    @classmethod
    def delete(self, key):
        """"Delete a plugin from DB"""
        for k in db.hgetall(key):
            db.hdel(key, k)

    @classmethod
    def create_from_zip(cls, zip_file):
        """Create a Plugin instance from a zipfile file object,
        can raise ValidationError"""
        metadata = dict(validator(zip_file))
        # Parse metadata
        key = cls.make_key(metadata['name'], metadata['version'])
        # Store
        db.hmset(key, metadata)
        zip_file.seek(0)
        db.hset(key, 'blob', zip_file.read())
        # Retrieve
        return Plugin(key)

    @classmethod
    def all(cls, orderby='title', version=None):
        plugins = []
        for key in db.scan_iter():
            if key.startswith('Plugin:'):
                plugin = Plugin(key)
                if (version is None
                    or isCompatible(version,
                                    plugin.qgisMinimumVersion,
                                    plugin.qgisMaximumVersion if
                                    plugin.qgisMaximumVersion else
                                    plugin.qgisMinimumVersion.split('.')[0]+'.99')):
                    plugins.append(plugin)
        return sorted(plugins, key=lambda p: getattr(p, orderby))

    def __init__(self, key):
        self.read(key)

    def __getattr__(self, k):
        try:
            return self.metadata[k]
        except KeyError:
            return ''

    def __nonzero__(self):
        return self is not None

    @property
    def key(self):
        return self.make_key(self.metadata['name'], self.metadata['version'])

    @property
    def title(self):
        return "{} - ver. {}".format(self.name, self.version)

    def incr_downloads(self):
        db.hincrby(self.key, 'downloads', 1)

    def write(self):
        """Write to db"""
        db.hmset(self.key, self.metadata)
        db.hset(self.key, 'blob', self.blob)


    def read(self, key):
        """Read from DB"""
        self.metadata = dict(db.hgetall(key).items())
        try:
            self.blob = self.metadata['blob']
        except:
            raise DoesNotExist
        del(self.metadata['blob'])


    def update_blob(self, k, v):
        zip = zipfile.ZipFile(StringIO(self.blob))
        metadata_name = [mn for mn in zip.namelist() if mn.endswith('metadata.txt')][0]
        parser = ConfigParser.ConfigParser()
        parser.optionxform = str
        parser.readfp(StringIO(codecs.decode(zip.read(metadata_name), "utf8")))
        parser.set('general', k, v)
        out = StringIO()
        parser.write(out)
        out.seek(0)
        outf = StringIO()
        zip_out = zipfile.ZipFile(outf, compression=zipfile.ZIP_DEFLATED, mode='w')
        for e in zip.namelist():
            if metadata_name != e:
                zip_out.writestr(e, zip.read(e))
        zip_out.writestr(metadata_name, out.read())
        zip_out.close()
        self.blob = outf.getvalue()
        self.write()

    def set_metadata(self, k, v):
        """Set a metadata value and calls write to save into the DB"""
        old_key = self.key
        self.metadata[k] = v
        # Set blob
        if k not in EXCLUDE_METADATA:
            self.update_blob(k, v)
        self.write()
        if old_key != self.key:
            self.delete(old_key)
