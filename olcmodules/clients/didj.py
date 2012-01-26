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
# didj.py Version 0.5
import os
import sys
from shlex import split as shlex_split
from subprocess import Popen, PIPE
from hashlib import md5
from shutil import copytree, rmtree
from time import sleep

class client(object):
    def __init__(self, mount_config, debug=False):
        self.debug = debug
        self._mount_config = mount_config
        self._didj_base = 'Base/'
        
        self._bootloader_dir = 'bootstrap-LF_LF1000'
        self._bootloader_files = ['lightning-boot.bin']
        
        self._firmware_dir = 'firmware-LF_LF1000'
        self._firmware_files = ['kernel.bin', 'erootfs.jffs2']
        
        self._cdb_cmds = {'lock':'C1', 'unlock':'C2', 'get_setting':'C3', 'disconnect':'C6'}
        self._settings = {'battery':'02', 'serial':'03', 'needs_repair':'06', 'None':'00'}
        self._battery_level = {'0':'Unknown' ,'1':'Critical' ,'2':'Low' ,'3':'Medium', '4':'High'}

        if sys.platform == 'win32':
            self._sg_raw = 'bin/sg_raw'
        else:
            self._sg_raw = 'sg_raw'
 
#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Didj Error: %s' % e



    def md5_files(self, file_list, lpath):
        try:
            for item in file_list:
                file_path = os.path.join(lpath, item)
                
                if os.path.exists(file_path):
                    f = open(file_path, 'rb')
                    md5h = md5()
                    md5h.update(f.read())
                    md5hash = md5h.hexdigest()
                    f.close()
                    md5_file_name = os.path.splitext(os.path.basename(file_path))[0]
                    md5_file_path = os.path.join(lpath, '%s.md5' % md5_file_name)
                    f = open(md5_file_path, 'wb')
                    f.write(md5hash)
                    f.close
            return True
        except Exception, e:
            self.error(e)



    def call_sg_raw(self, cmd, arg='None', buf_len=0):
        try:
            
            if len(self._settings[arg]) == 0:
                self.error('Bad settings value')                    
            elif len(self._cdb_cmds[cmd]) == 0:
                self.error('Bad command')
                
            if buf_len:
                buf_len = '-r%s -b' % buf_len
            else:
                buf_len = ''
                
            cmdl = '%s %s %s %s %s 00 00 00 00 00 00 00 00' % (self._sg_raw, buf_len, self._mount_config.device_id, self._cdb_cmds[cmd], self._settings[arg])
            cmd = shlex_split(cmdl)
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            err = p.stderr.read()
            
            if not 'Good' in err:
                if arg != 'None':
                    return False
                else:
                    self.error('SCSI error.')
                
            if arg != 'None':
                sleep(1)
                return p.stdout.read()      
        except Exception, e:
            self.error(e)



    def get_update_paths(self, lpath, type_dir):
        try:
            if lpath[-1:] == '/':
                lpath = lpath[0:-1]

            if not os.path.basename(lpath) == type_dir:
                if os.path.exists(os.path.join(lpath, type_dir)):
                    lpath = os.path.join(lpath, type_dir)
                else:
                    self.error('Firmware directory not found.')

            rpath = os.path.join(self._mount_config.host_id, self._didj_base)
            
            if not os.path.exists(rpath):
                self.error('Could not find Base/ path on device.')
            else:
                rpath = os.path.join(rpath, type_dir)
                    
            return [lpath, rpath]
        except Exception, e:
            self.error(e)



    def move_update(self, lpath, rpath):
        try:
            if os.path.exists(lpath) and os.path.exists(os.path.dirname(rpath)):
                if self.debug:
                    print '\n-------------------'
                    print 'local: %s' % lpath
                    print 'remote: %s' % rpath
                    print '\n'
                else:                
                    copytree(lpath, rpath)
            else:
                self.error('One of the paths does not exist')
        except Exception, e:
            self.error(e)



    def get_battery_value(self):
        try:
            ret = self.call_sg_raw('get_setting', 'battery', 1)
            if ret:
                return ord(ret)
            else:
                return 0
        except Exception, e:
            self.error(e)
            
#######################
# Client User Didj Information Functions
#######################

    def get_battery_level(self):
        try:
            ret = str(self.get_battery_value())
            return self._battery_level[ret]
        except Exception, e:
            self.rerror(e)
    battery_level = property(get_battery_level)



    def get_serial_number(self):
        try:
            ret = self.call_sg_raw('get_setting', 'serial', 16)
            ret_arr = [ord(i) for i in ret]
            if not 0 in ret_arr:
                return ret
            else:
                return 'Unknown'
        except Exception, e:
            self.rerror(e)
    serial_number = property(get_serial_number)



    def get_needs_repair(self):
        try:
            ret = self.call_sg_raw('get_setting', 'needs_repair', 1)
            if ret:
                return True
            else:
                return False

        except Exception, e:
            self.rerror(e)
    needs_repair = property(get_needs_repair)
 
#######################
# Client User Command Functions
#######################

    def umount(self):
        try:
            self.call_sg_raw('lock')
        except Exception, e:
            self.rerror(e)



    def mount(self):
        try:
            self.call_sg_raw('unlock')
        except Exception, e:
            self.rerror(e)



    def eject(self):
        try:
            self.call_sg_raw('disconnect')
            if not sys.platform == 'win32':
                print 'Please eject the device from your system.'
        except Exception, e:
            self.rerror(e)



    def upload_firmware(self, lpath):
        try:
            lpath, rpath = self.get_update_paths(lpath, self._firmware_dir)
            self.md5_files(self._firmware_files, lpath)
            
            if os.path.exists(rpath):
                self.error('Found %s on device already.' % self._firmware_dir)
            
            self.move_update(lpath, rpath)
        except Exception, e:
            self.rerror(e)



    def upload_bootloader(self, lpath):
        try:
            lpath, rpath = self.get_update_paths(lpath, self._bootloader_dir)
            self.md5_files(self._bootloader_files, lpath)
            
            if os.path.exists(rpath):
                self.error('Found %s on device already.' % self._bootloader_dir)
            
            self.move_update(lpath, rpath)
        except Exception, e:
            self.rerror(e)


    def cleanup(self):
        try:
            rpath = os.path.join(self._mount_config.host_id, self._didj_base)
            
            if not os.path.exists(rpath):
                self.error('Could not find Base/ path on device.')
            else:
                fwpath = os.path.join(rpath, self._firmware_dir)
                blpath = os.path.join(rpath, self._bootloader_dir)
                
                if os.path.exists(fwpath):            
                    if self.debug:
                        print '\n-------------------'
                        print 'firware path: %s' % fwpath
                        print '\n'
                    else:
                        rmtree(fwpath)
                    
                if os.path.exists(blpath):          
                    if self.debug:
                        print '\n-------------------'
                        print 'bootloader path: %s' % blpath
                        print '\n'
                    else:                
                        rmtree(blpath)               
        except Exception, e:
            self.rerror(e)
