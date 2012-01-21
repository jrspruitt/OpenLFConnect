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
# Version: Version 0.4
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform
##############################################################################

import os
import sys
from shutil import copytree, copyfile
from time import sleep
from subprocess import Popen, PIPE

if sys.platform == 'win32':
    import win32api

class config(object):
    def __init__(self, dev_id='', mount_point='', debug=False):
        self.debug = debug
        self._linux_dev = '/dev/leapfrog'
        self._vendor_name = 'leapfrog'
        self._dev_id = dev_id
        self._mount_point = mount_point
        
        self._time_out = 30

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



    def find_dev_id(self):
        try:
            time_out = self._time_out
            while time_out:
                if not os.path.exists(self._linux_dev):
                    p = Popen(self._sg_scan, stdout=PIPE, stderr=PIPE)
                    err = p.stderr.read()
    
                    if not err:
                        ret = p.stdout.read()
                        lines = ret.split('\n')
                        
                        for line in lines:
                        
                            if line.strip().lower().find(self._vendor_name) != -1:
                                if sys.platform == 'win32':
                                    self.dev_id = '%s' % line.split(' ')[0]
                                else:
                                    self.dev_id = '%s' % lines[lines.index(line) -1].split(' ')[0].replace(':', '')
    
                                return self.dev_id

                else:
                    self.dev_id = self._linux_dev
                    return self.dev_id
                
                time_out -= 1
                sleep(1)
                                
            self.error('Device not found.')
        except Exception, e:
            self.rerror(e)



    def find_mount_point(self, win_label='didj'):
        try:
            index = 10
            
            while index:
                if sys.platform == 'win32':
                    drive_list = win32api.GetLogicalDriveStrings()
                    drive_list = drive_list.split('\x00')[1:]
                    
                    for drive in drive_list:
                    
                        try:
                            info = win32api.GetVolumeInformation(drive)[0]
                            if info.lower() == win_label:
                                self.mount_point = '%s' % drive
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
                sleep(1)
                index -= 1
            self.error('Mount not found.')
        except Exception, e:
            self.rerror(e)



#######################
# User functions
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



    def is_connected(self):
        try:
            if os.path.exists(self.mount_point):
                return True
            else:
                return False
        except Exception, e:
            self.rerror(e)
        
            

class client(object):
    def __init__(self, debug):
        self.debug = debug
    

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
# Filesystem User functions
#######################



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



    def mkdir(self, path):
        try:
            if not os.path.exists(path):
                if self.debug:
                    print '\n-------------------'
                    print 'made: %s' % path
                    print '\n'
                else:
                    os.mkdir(path)
            else:
                self.error('Directory already exists')
        except Exception, e:
            self.rerror(e)



    def rmdir(self, path):
        try:
            if os.path.exists(path):
                if self.debug:
                    print '\n-------------------'
                    print 'removed: %s' % path
                    print '\n'
                else:
                    os.rmdir(path)
        except Exception, e:
            self.rerror(e)



    def rm(self, path):
        try:
            if os.path.exists(path):
                if self.debug:
                    print '\n-------------------'
                    print 'Removed: %s' % path
                    print '\n'
                else:
                    os.remove(path)
            else:
                self.error('File does not exist')
        except Exception, e:
            self.rerror(e)



    def upload_file(self, lpath, rpath):
        try:
            if not os.path.exists(lpath):
                self.error('Path does not exist.')
                
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote: %s' % rpath
                print '\n'
            else:
                copyfile(lpath, rpath)
                print 'Uploaded %s bytes' % os.path.getsize(rpath)
        except Exception, e:
            self.rerror(e)



    def upload_dir(self, lpath, rpath):
        try:
            if os.path.exists(lpath):
                
                if self.debug:
                    print '\n-------------------'
                    print 'local: %s' % lpath
                    print 'remote %s' % rpath
                    print '\n'
                else:
                    copytree(lpath, rpath)
                    print 'Uploaded %s bytes' % os.path.getsize(rpath)
        except Exception, e:
            self.rerror(e)



    def download_file(self, lpath, rpath):
        try:
            if not os.path.exists(rpath):
                self.error('Path does not exist.')
                
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote: %s' % rpath
                print '\n'
            else:
                copyfile(rpath, lpath)
                print 'Downloaded %s bytes' % os.path.getsize(lpath)
        except Exception, e:
            self.rerror(e)


    def cat(self, path):
        try:
            f = open(path, 'r')
            buf = f.read()
            f.close()
            return buf
        except Exception, e:
            self.rerror(e)