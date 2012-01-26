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
# Version: Version 0.6
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
# local.py Version 0.5
import os
from shutil import copytree, copyfile, rmtree


class client(object):
    def __init__(self, debug):
        self.debug = debug

#######################
# Filesystem Internal Functions
#######################

    def file_check(self, path):
        try:
            if os.path.exists(path):
                if not os.path.isdir(path):
                    return True
                else:
                    self.error('Path is not a file.')
            else:
                    self.error('Path does not exist.')
                
        except Exception, e:
            self.error(e)



    def dir_check(self, path):
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    return True
                else:
                    self.error('Path is not a directory.')
            else:
                    self.error('Path does not exist.')
                
        except Exception, e:
            self.error(e)
            
#######################
# Filesystem Interface Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Local FS Error: %s' % e



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
            if self.debug:
                print '\n-------------------'
                print 'Made: %s' % path
                print '\n'
            else:
                os.mkdir(path)

        except Exception, e:
            self.error(e)



    def rmdir_i(self, path):
        try:
            if self.debug:
                print '\n-------------------'
                print 'removed: %s' % path
                print '\n'
            else:
                rmtree(path)
                
        except Exception, e:
            self.error(e)



    def rm_i(self, path):
        try:
            if self.debug:
                print '\n-------------------'
                print 'Removed: %s' % path
                print '\n'
            else:
                os.remove(path)
                
        except Exception, e:
            self.error(e)



    def download_file_i(self, lpath, rpath):
        try:
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote: %s' % rpath
                print '\n'
            else:
                copyfile(rpath, lpath)
                print 'Downloaded %s bytes' % os.path.getsize(lpath)
        except Exception, e:
            self.error(e)



    def download_dir_i(self, lpath, rpath):
        try:
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote: %s' % rpath
                print '\n'
            else:
                copytree(rpath, lpath)
                print 'Downloaded %s' % os.path.basename(lpath)
        except Exception, e:
            self.error(e)



    def upload_file_i(self, lpath, rpath):
        try:
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote: %s' % rpath
                print '\n'
            else:
                copyfile(lpath, rpath)
                print 'Uploaded %s: %s Bytes' % (os.path.basename(lpath), os.path.getsize(lpath))
        except Exception, e:
            self.error(e)



    def upload_dir_i(self, lpath, rpath):
        try:
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote %s' % rpath
                print '\n'
            else:
                copytree(lpath, rpath)
                print 'Uploaded %s' % os.path.basename(lpath)
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

#######################
# Filesystem Interface Functions
# Input Checks
#######################

    def rfile_check_i(self, path):
        return self.file_check(path)

    def rdir_check_i(self, path):
        return self.dir_check(path)

    def lfile_check_i(self, path):
        return self.file_check(path)

    def ldir_check_i(self, path):
        return self.dir_check(path)
            
if __name__ == '__main__':
    print 'No examples yet.'