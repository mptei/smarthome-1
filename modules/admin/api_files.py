#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################


import os
import datetime
import logging
import json
import cherrypy

import lib.backup
from lib.item import Items
from .rest import RESTResource

import bin.shngversion
from lib.item_conversion import convert_yaml as convert_yaml
from lib.item_conversion import parse_for_convert as parse_for_convert
from lib.shtime import Shtime


# ======================================================================
#  Controller for REST API /api/files
#
class FilesController(RESTResource):
    """
    Controller for REST API /api/files
    """

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.etc_dir = self._sh._etc_dir
        self.items_dir = self._sh._items_dir
        self.logics_dir = self._sh._logic_dir
        self.extern_conf_dir = self._sh._extern_conf_dir
        self.modules_dir = os.path.join(self.base_dir, 'modules')
        return


    def get_body(self, text=False):
        """
        Get content body of received request header (for file uploads)

        :return:
        """
        cl = cherrypy.request.headers.get('Content-Length', 0)
        if cl == 0:
            # cherrypy.reponse.headers["Status"] = "400"
            # return 'Bad request'
            raise cherrypy.HTTPError(status=411)
        rawbody = cherrypy.request.body.read(int(cl))
        self.logger.debug("ServicesController(): get_body(): rawbody = {}".format(rawbody))
        try:
            if text:
                params = rawbody.decode('utf-8')
            else:
                params = json.loads(rawbody.decode('utf-8'))
        except Exception as e:
            self.logger.warning("ServicesController(): get_body(): Exception {}".format(e))
            return None
        return params


    # def strip_empty_lines(self, txt):
    #     """
    #     Remove \r from text and remove exessive empty lines from end
    #     """
    #     txt = txt.replace('\r', '').rstrip()
    #     while txt.endswith('\n'):
    #         txt = txt[:-1].rstrip()
    #     txt += '\n\n'
    #     #        self.logger.warning("strip_empty_lines: txt = {}".format(txt))
    #     return txt


    # ======================================================================
    #  /api/files/logging
    #
    def get_logging_config(self):

        self.logger.info("FilesController.get_logging_config()")
        filename = os.path.join(self.etc_dir, 'logging.yaml')
        read_data = None
        with open(filename) as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', 'logging.yaml')


    def save_logging_config(self):
        """
        Save logging configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_logging_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_logging_config(): '{}'".format(params))


        filename = os.path.join(self.etc_dir, 'logging.yaml')
        read_data = None
        with open(filename, 'w') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/structs
    #
    def get_struct_config(self):

        self.logger.info("FilesController.get_struct_config()")
        filename = os.path.join(self.etc_dir, 'struct.yaml')
        if not(os.path.isfile(filename)):
            open(filename, 'a').close()
            self.logger.info("FilesController.get_struct_config(): created empty file {}".format(filename))

        read_data = None
        with open(filename) as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', 'struct.yaml')


    def save_struct_config(self):
        """
        Save struct configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_struct_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_struct_config(): '{}'".format(params))


        filename = os.path.join(self.etc_dir, 'struct.yaml')
        read_data = None
        with open(filename, 'w') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/items
    #
    def get_items_filelist(self):

        list = os.listdir( self.items_dir )
        filelist = []
        for filename in list:
            if filename.endswith('.yaml'):
                filelist.append(filename)
            if filename.endswith('.conf'):
                filelist.append(filename)

        self.logger.info("filelist = {}".format(filelist))
        self.logger.info("filelist.sort() = {}".format(filelist.sort()))
        return json.dumps(sorted(filelist))


    def get_items_config(self, fn):

        self.logger.info("FilesController.get_items_config({})".format(fn))
        filename = os.path.join(self.items_dir, fn + '.yaml')
        read_data = None
        with open(filename) as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', fn + '.yaml')


    def save_items_config(self, filename):
        """
        Save items configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController(): save_items_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController(): save_items_config(): '{}'".format(params))


        filename = os.path.join(self.items_dir, filename + '.yaml')
        read_data = None
        with open(filename, 'w') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/logics
    #
    def get_logics_filelist(self):

        list = os.listdir( self.logics_dir )
        filelist = []
        for filename in list:
            if filename.endswith('.py'):
                filelist.append(filename)

        self.logger.info("filelist = {}".format(filelist))
        self.logger.info("filelist.sort() = {}".format(filelist.sort()))
        return json.dumps(sorted(filelist))


    def get_logics_config(self, fn):

        self.logger.info("FilesController.get_logics_config({})".format(fn))
        filename = os.path.join(self.logics_dir, fn)
        read_data = None
        with open(filename) as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', fn)


    def save_logics_config(self, filename):
        """
        Save items configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_logics_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_logics_config(): '{}'".format(params))


        filename = os.path.join(self.logics_dir, filename)
        read_data = None
        with open(filename, 'w') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/...
    #
    def cachecheck(self):
        """
        returns a list of items as json structure
        """
        unused_cache_files = []

        if self._sh.shng_status['code'] == 20:
            # {'code': 20, 'text': 'Running'}
            cache_path = os.path.join(self.base_dir, 'var', 'cache')
            onlyfiles = [f for f in os.listdir(cache_path) if os.path.isfile(os.path.join(cache_path, f))]

            for file in onlyfiles:
                if not file.find(".") == 0:  # filter .gitignore etc.
                    self.items = Items.get_instance()
                    item = self.items.return_item(file)
                    no_cache_file = False;
                    if item is None:
                        self.logger.debug("cachecheck: no item {}".format(file))
                        no_cache_file = True
                    elif not item._cache:
                        self.logger.debug("cachecheck: item {}, no _cache".format(file))
                        no_cache_file = True

                    if no_cache_file:
                        file_data = {}
                        file_data['last_modified'] = datetime.datetime.fromtimestamp(
                            int(os.path.getmtime(os.path.join(cache_path, file)))
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        file_data['created'] = datetime.datetime.fromtimestamp(
                            int(os.path.getctime(os.path.join(cache_path, file)))
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        file_data['filename'] = file
                        file_data['filename'] = file
                        unused_cache_files.append(file_data)

        return json.dumps(unused_cache_files)

    # --------------------------------------------------------------------------------------

    def get_config_backup(self):

        filename = lib.backup.create_backup(self.extern_conf_dir)
        read_data = None
        with open(filename, 'rb') as f:
            read_data = f.read()

        return read_data


    def get_config_backup2(self):

        filename = lib.backup.create_backup(self.extern_conf_dir)

        return cherrypy.lib.static.serve_file(filename, 'application/zip',
                                 'attachment', 'shng_backup.zip')


    # ======================================================================
    #  GET /api/services/
    #
    def read(self, id='', filename=''):
        """
        Handle GET requests for server API
        """
        self.logger.info("FilesController.read(id='{}', filename='{}')".format(id, filename))

        if id == 'logging':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_logging_config()
        elif id == 'structs':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_struct_config()
        elif (id == 'items' and filename == ''):
            return self.get_items_filelist()
        elif id == 'items':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_items_config(filename)
        elif (id == 'logics' and filename == ''):
            return self.get_logics_filelist()
        elif id == 'logics':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_logics_config(filename)
        elif id == 'backup':
            return self.get_config_backup()
        return None

    read.expose_resource = True
    read.authentication_needed = True


    def update(self, id='', filename=''):
        """
        Handle PUT requests for server API
        """
        self.logger.info("FilesController.update(id='{}', filename='{}')".format(id, filename))

        if id == 'logging':
            return self.save_logging_config()
        elif id == 'structs':
            return self.save_struct_config()
        elif (id == 'items' and filename != ''):
            return self.save_items_config(filename)
        elif (id == 'logics' and filename != ''):
            return self.save_logics_config(filename)

        return None

    update.expose_resource = True
    update.authentication_needed = True

