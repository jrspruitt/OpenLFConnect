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
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
# local.py Version 0.7
import os
from shutil import copyfile, rmtree
from olcmodules.config import debug as dbg

class client(object):
    def __init__(self, debug):
        self.debug = debug
        self._dbg = dbg(self)

#######################
# Filesystem Interface Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, ' Local FS Error: %s' % e



    def exists_i(self, path):
        try:
            if os.path.exists(path):
                return True
            else:
                return False
        except Exception, e:
            self.error(e)



    def is_dir_i(self, path):
        try:
            return os.path.isdir(path)
        except Exception, e:
            self.error(e)



    def dir_list_i(self, path):
        try:
            dir_list = []
            dir_arr = os.listdir(path)
            if dir_arr:
                for item in dir_arr:
                    if os.path.isdir(os.path.join(path, item)):
                        dir_list.append('%s/' % item)
                    else:
                        dir_list.append(item)
                        
                return dir_list
            else:
                return ''
        except Exception, e:
            self.error(e)



    def mkdir_i(self, path):
        try:
            if not self._dbg.make(path):
                os.mkdir(path)

        except Exception, e:
            self.error(e)



    def rmdir_i(self, path):
        try:
            if not self._dbg.remove(path):
                rmtree(path)
                
        except Exception, e:
            self.error(e)



    def rm_i(self, path):
        try:
            if not self._dbg.remove(path):
                os.remove(path)
                
        except Exception, e:
            self.error(e)



    def download_file_i(self, lpath, rpath, tab=' '):
        try:
            if not self._dbg.download(lpath, rpath):
                copyfile(rpath, lpath)
                print '%s%s: %s Bytes' % (tab, os.path.basename(lpath), os.path.getsize(lpath))
        except Exception, e:
            self.error(e)



    def download_dir_i(self, lpath, rpath, tab=' '):
        try:
            if not os.path.exists(lpath) and not self._dbg.make(lpath):
                os.mkdir(lpath)
                print '%s%s/' % (tab, os.path.basename(lpath))
                tab+=' '
                    
            for item in self.dir_list_i(rpath):
                if item != './' and item != '../':
                    item_lpath = os.path.normpath(os.path.join(lpath, item))
                    item_rpath = os.path.join(rpath, item).replace('\\', '/')
                    rexists = self.exists_i(item_rpath)
                    
                    if rexists and self.is_dir_i(item_rpath):
                        if not os.path.exists(lpath) and not self._dbg.make(item_lpath):
                            os.mkdir(item_lpath)
                            print '%s%s/' % (tab, os.path.basename(item_lpath))
                            
                        self.download_dir_i(item_lpath, item_rpath, tab)

                    elif rexists and not self.is_dir_i(item_rpath):
                        self.download_file_i(item_lpath, item_rpath, tab)
                        
                    else:
                        print '%sSkipped: %s' % (tab, item_rpath)
        except Exception, e:
            self.error(e)



    def upload_file_i(self, lpath, rpath, tab=' '):
        try:
            if not self._dbg.upload(lpath, rpath):
                copyfile(lpath, rpath)
                print '%s%s: %s Bytes' % (tab, os.path.basename(lpath), os.path.getsize(lpath))
        except Exception, e:
            self.error(e)



    def upload_dir_i(self, lpath, rpath, tab=' '):
        try:
            if not self.exists_i(rpath) and not self._dbg.make(rpath):
                self.mkdir_i(rpath)
                print '%s%s/' % (tab, os.path.basename(rpath))
                tab+=' '
          
            for item in os.listdir(lpath):
                item_lpath = os.path.join(lpath, item)
                item_rpath = os.path.join(rpath, item).replace('\\', '/')
                lexists = os.path.exists(item_lpath)
                
                if lexists and os.path.isdir(item_lpath):
                    if self.exists_i(item_rpath) and not self._dbg.make(item_rpath):
                        self.mkdir_i(item_rpath)
                        print '%s%s/' % (tab, os.path.basename(item_rpath))

                    self.upload_dir_i(item_lpath, item_rpath, tab)

                elif lexists and not os.path.isdir(item_lpath):
                    self.upload_file_i(item_lpath, item_rpath, tab)

                else:
                    print '%sSkipped: %s' % (tab, item_lpath)
        except Exception, e:
            self.error(e)



    def cat_i(self, path):
        try:
            f = open(path, 'r')
            buf = f.read()
            f.close()
            return buf
        except Exception, e:
            self.error(e)
            
if __name__ == '__main__':
    print 'No examples yet.'