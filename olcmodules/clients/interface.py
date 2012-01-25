#!/usr/bin/env python
##############################################################################
#    OpenLFConnect
#
#    Copyright (c) 2012 Jason Pruitt <jrspruitt@gmail.com>
#
#    This file is part of OpenLFConnect.
#    OpenLFConnect is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenLFConnect is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenLFConnect.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################



##############################################################################
# Title:   OpenLFConnect
# Version: Version 0.5
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
class filesystem(object):
    
    def __init__(self, client):
        self._client = client



    def get_debug(self):
        return self._client.debug
    
    def set_debug(self, debug):
        self._client.debug = debug

    debug = property(get_debug, set_debug)



    def exists(self, path):
        try:
            if self._client.exists_i(path):
                return True
            else:
                self._client.error('Path does not exist.')
        except Exception, e:
            self._client.rerror(e)



    def is_dir(self, path):
        try:
            if self._client.exists_i(path):
                return self._client.is_dir_i(path)
            else:
                self._client.error('Path does not exist.')
        except Exception, e:
            self._client.rerror(e)



    def dir_list(self, path):
        try:
            if self._client.rdir_check_i(path):
                return self._client.dir_list_i(path)
        except Exception, e:
            self._client.rerror(e)



    def mkdir(self, path):
        try:            
            if not self._client.exists_i(path):
                self._client.mkdir_i(path)
            else:
                self._client.error('Directory already exists.')
                
        except Exception, e:
            self._client.rerror(e)



    def rmdir(self, path):
        try:
            if self._client.rdir_check_i(path):
                self._client.rmdir_i(path)
                
        except Exception, e:
            self._client.rerror(e)



    def rm(self, path):
        try:
            if self._client.rfile_check_i(path):
                self._client.rm_i(path)
                
        except Exception, e:
            self._client.rerror(e)



    def download_file(self, lpath, rpath):
        try:
            if self._client.rfile_check_i(rpath):
                self._client.download_file_i(lpath, rpath)                

        except Exception, e:
            self._client.rerror(e)



    def download_dir(self, lpath, rpath):
        try:
            if self._client.rdir_check_i(rpath):
                self._client.download_dir_i(lpath, rpath)
                
        except Exception, e:
            self._client.rerror(e)



    def upload_file(self, lpath, rpath):
        try:
            if self._client.lfile_check_i(lpath):
                self._client.upload_file_i(lpath, rpath)
                
        except Exception, e:
            self._client.rerror(e)



    def upload_dir(self, lpath, rpath):
        try:
            if self._client.ldir_check_i(lpath):
                self._client.upload_dir_i(lpath, rpath)
                
        except Exception, e:
            self._client.rerror(e)



    def cat(self, path):
        try:
            if self._client.rfile_check_i(path):
                return self._client.cat_i(path)
                
        except Exception, e:
            self._client.rerror(e)
                   
if __name__ == '__main__':
    print 'No examples yet.'