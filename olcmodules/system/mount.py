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
# mount.py Version 0.5.2
import os
import re
import sys
from time import sleep
from subprocess import Popen, PIPE

class connection(object):
    def __init__(self, device_id='', mount_point='', debug=False):
        self.debug = debug

        self._linux_dev = '/dev/leapfrog'
        self._linux_mount_dir = '/media'
        
        self._vendor_name = 'leapfrog'
        
        self._time_out = 30

        if sys.platform == 'win32':
            self._sg_scan = ['bin/sg_scan']
            self._dev_regex = r'^PD[\d]{1,2}$'
            self._mount_regex = r'^[a-zA-Z]{1}:\\$'
        else:
            self._sg_scan = ['sg_scan', '-i']
            self._dev_regex = r'^/dev/[\w/]+$'
            self._mount_regex = r'^%s/[\w/]+$' % self._linux_mount_dir

        if device_id != '':
            if self.check_device_id(device_id):
                self._device_id = device_id
            else:
                self.rerror('Malformed device id.')
        else:
            self._device_id = device_id
        
        if mount_point == 'NULL':
            self._mount_point = '/'
        elif mount_point != '':
            if self.check_mount_point(mount_point):
                self._mount_point = mount_point
            else:
                self.rerror('Malformed mount point name')
        else:
            self._mount_point = mount_point
    

#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Mount Error: %s' % e



    def check_device_id(self, did):
        regex_did = re.compile(self._dev_regex)
        if regex_did.search(did):
            return True
        else:
            return False



    def check_mount_point(self, mount):
        regex_mount = re.compile(self._mount_regex)
        if regex_mount.search(mount):
            return True
        else:
            return False



    def sg_scan(self):
        try:
            p = Popen(self._sg_scan, stdout=PIPE, stderr=PIPE)
            err = p.stderr.read()
            
            if not err:
                ret = p.stdout.read()
                
                if self._vendor_name in ret.lower():
                    return ret
                else:
                    return ''
            else:
                return ''
        except Exception, e:
            self.error(e)



    def find_device_id(self):
        try:
            time_out = self._time_out

            while time_out:
                if sys.platform == 'win32':
                    lines = self.sg_scan().split('\n')
                    if lines:
                        for line in lines:
                            if self._vendor_name in line.lower():
                                if sys.platform == 'win32':
                                    self._device_id = '%s' % line.split(' ')[0]
                                else:
                                    #print lines[lines.index(line) -1] delete after testing didj, why here?
                                    self._device_id = '%s' % lines[lines.index(line) -1].split(' ')[0].replace(':', '')
                
                                return self._device_id

                elif not os.path.exists(self._linux_dev):
                    vendor_pattern = '/sys/class/scsi_disk/%s:0:0:0/device/vendor'
                    blockdev_pattern = '/sys/class/scsi_disk/%s:0:0:0/device/block'

                    for i in range(0, 100):
                        vendor_path = vendor_pattern % (i)

                        if os.path.exists(vendor_path):
                            f = open(vendor_path, 'r')
                            vendor = f.readline()
                            f.close()

                            if vendor.rstrip().lower() == 'leapfrog':
                                for sdx in os.listdir(blockdev_pattern % i):

                                    if sdx.startswith('sd'):
                                        self._device_id = '/dev/%s' % sdx
                                        return self._device_id
                else:
                    self._device_id = self._linux_dev
                    return self._device_id
                                                        
                time_out -= 1
                sleep(1)
            self.error('Device not found.')
        except Exception, e:
            self.error(e)



    def find_mount_point(self, win_label='didj'):
        try:
            timeout = 10
            
            while timeout:
                if sys.platform == 'win32':
                    lines = self.sg_scan()
                    if lines:
                        for line in lines.split('\n'):
                            if self._vendor_name in line.lower():
                                mount_regex = re.compile(r'\[(?P<mp>[a-zA-Z]{1})\]')
                                drv = mount_regex.search(line)

                                if drv:
                                    self._mount_point = '%s:\\' % drv.group('mp')
                                    return self._mount_point
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
                timeout -= 1
            self.error('Mount not found.')
        except Exception, e:
            self.error(e)



#######################
# Connection Interface functions
#######################

    def get_root_dir_i(self):
        return self.get_host_id_i()

    

    def get_device_id_i(self):
        try:
            return self._device_id or self.find_device_id()
        except Exception, e:
            self.error(e)



    def get_host_id_i(self):
        try:
            return self._mount_point or self.find_mount_point()
        except Exception, e:
            self.error(e)



    def is_connected_i(self):
        try:
            return os.path.exists(self._mount_point)
        except Exception, e:
            self.error(e)

if __name__ == '__main__':
    print 'No examples yet.'