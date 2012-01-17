#!/usr/bin/env python
##############################################################################
#    OpenLFConnect verson 0.2
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

# OpenLFConnect version 0.2

import os
import sys
import subprocess
import shutil
import time

if sys.platform == 'win32':
    import win32api


class filesystem(object):
    def __init__(self):
        self._linux_dev = '/dev/leapfrog'
        self._vendor_name = 'leapfrog'
        self._dev_id = ''
        self._mount_point = ''

        if sys.platform == 'win32':
            self._sg_scan = ['bin/sg_scan']
        else:
            self._sg_scan = ['sg_scan', '-i']
    

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

    def set_dev_id(self, dev_id):
        self._dev_id = dev_id

    def get_dev_id(self):
        return self._dev_id or self.find_dev_id()

    dev_id = property(get_dev_id, set_dev_id)



    def set_mount_point(self, mount_point):
        self._mount_point = mount_point

    def get_mount_point(self):
        return self._mount_point or self.find_mount_point()
    
    mount_point = property(get_mount_point, set_mount_point)



    def find_dev_id(self):
        try:
            if not os.path.exists(self._linux_dev):
                child = subprocess.Popen(self._sg_scan, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                err = child.stderr.read()

                if not err:
                    ret = child.stdout.read()
                    lines = ret.split('\n')
                    
                    for line in lines:
                        if sys.platform == 'win32':
                            if line.lower().find(self._vendor_name) != -1:
                                self.dev_id = '%s' % line.split(' ')[0]
                                return self.dev_id
                        else:
                            if line.strip().lower().find(self._vendor_name) != -1:
                                self.dev_id = '%s' % lines[lines.index(line) -1].split(' ')[0].replace(':', '')
                                return self.dev_id
                            
                    self.error('Device not found')
                else:
                    self.error(err)
                    
            else:
                self.dev_id = self._linux_dev
                return self.dev_id
        except Exception, e:
            self.rerror(e)



    def find_mount_point(self, win_label='didj'):
        try:
            index = 10
            
            while index:
                if sys.platform == 'win32':
                    drive_list = win32api.GetLogicalDriveStrings()
                    drive_list = drive_list.split('\\\x00')[1:]
                    
                    for drive in drive_list:
                        try:
                            info = win32api.GetVolumeInformation(drive)[0]
                            if info.lower() == win_label:
                                self.mount_point = '%s\\' % drive
                                return self.mount_point
                        except: pass
                else:
                    syspath = '/sys/class/scsi_disk'
                    
                    for device in os.listdir(syspath):
                        f = open(os.path.join(syspath, device, 'device/vendor'), 'r')
                        vendor = f.read().split('\n')[0]
                        f.close()
                        
                        if vendor.lower() == self._vendor_name:
                            dev_path = '/dev/%s' % os.listdir(os.path.join(syspath, device, 'device/block'))[0]
                           
                            f = open('/proc/mounts', 'r')
                            
                            for line in f:
                                if line.startswith(dev_path):
                                    self._mount_point = line.split(' ')[1]
                                    f.close()
                                    return self._mount_point
                            f.close()
                time.sleep(1)
                index -= 1
            self.error('Mount not found.')
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
