#!/usr/bin/env python
##############################################################################
#    OpenLFConnect verson 0.1
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

# OpenLFConnect version 0.1.0

import os
import sys
import subprocess
import shutil
if sys.platform == 'win32':
    import win32api


class filesystem(object):
    def __init__(self):
        self._linux_dev = '/dev/leapfrog'
        if sys.platform == 'win32':
            self._sg_scan = 'bin/sg_scan'
            self._mount_base = ''
        else:
            self._sg_scan = 'sg_scan'
            self._mount_base = '/media'
    

#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Local FS Error: %s' % e


    def exists(self, path):
        try:
            if os.path.exists(path):
                return True
            else:
                self.error('Directory does not exist')
        except Exception, e:
            self.error(e)



#######################
# Filesystem functions
#######################

    def get_device_id(self):
        try:
            if not os.path.exists(self._linux_dev):
                child = subprocess.Popen([self._sg_scan], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                err = child.stderr.read()
                if not err:
                    ret = child.stdout.read()
                    lines = ret.split('\n')
                    for line in lines:
                        if line.lower().find('leapfrog') != -1:
                            return '%s' % line.split(' ')[0]
                    self.error('Device not found')
                else:
                    self.error(err)
            else:
                return self._linux_dev
        except Exception, e:
            self.rerror(e)



    def get_mount_path(self, mount_name):
        try:
            if sys.platform == 'win32':
                drive_list = win32api.GetLogicalDriveStrings()
                drive_list = drive_list.split('\\\x00')[1:]
                for drive in drive_list:
                    try:
                        info = win32api.GetVolumeInformation(drive)[0]
                        if info.lower() == mount_name.lower():
                            return '%s\\' % drive
                    except: pass
                return self.error('Mount not found.')
            else:
                for item in os.listdir(self._mount_base):
                    if os.path.basename(mount_name).lower() == item.lower() and os.path.isdir(os.path.join(self._mount_base, item)):
                        return os.path.join(self._mount_base, item)
                return self.error('Mount not found.')
        except Exception, e:
            self.rerror(e)



    def dir_list(self, path):
        try:
            dir_list = []        
            if self.exists(path):
                for item in os.listdir(path):
                    if os.path.isdir(os.path.join(path, item)):
                        dir_list.append('%s/' % item)
                    else:
                        dir_list.append(item)
                        
                return dir_list
        except Exception, e:
            self.rerror(e)


    def is_dir(self, path):
        try:
            return os.path.isdir(path)
        except Exception, e:
            self.rerror(e)


    def cpdir(self, src, dst):
        try:
            if os.path.exists(src):
                shutil.copytree(src, dst)
        except Exception, e:
            self.rerror(e)



    def cp(self, src, dst):
        try:
            if os.path.exists(src):
                shutil.copy(src, dst)
        except Exception, e:
            self.rerror(e)



    def mkdir(self, path):
        try:
            if not os.path.exists(path):
                os.mkdir(path)
            else:
                self.error('Directory already exists')
        except Exception, e:
            self.rerror(e)



    def rmdir(self, path):
        try:
            if os.path.exists(path):
                os.rmdir(path)
            else:
                self.error('Directory does not exist')
        except Exception, e:
            self.rerror(e)



    def rm(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
            else:
                self.error('File does not exist')
        except Exception, e:
            self.rerror(e)
