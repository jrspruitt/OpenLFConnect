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
# client.didj.py Version 0.8.1
import os
import sys
from shlex import split as shlex_split
from subprocess import Popen, PIPE
from shutil import rmtree, copy
from time import sleep
from olcmodules.config import debug as dbg

import olcmodules.firmware.didj as fwdidj

class client(object):
    def __init__(self, mount_config, debug=False):
        self.debug = debug
        self._dbg = dbg(self)
        
        self._mount_config = mount_config
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



    def move_update(self, paths):
        try:
            for lpath, rpath in paths:
                if os.path.exists(lpath) and os.path.exists(os.path.dirname(rpath)):
                    if not self._dbg.upload(lpath, rpath):
                        copy(lpath, rpath)
                elif self.debug:
                    self._dbg.upload(lpath, rpath)
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



    def sync(self):
        if sys.platform != 'win32':
            p = Popen(['sync'], stderr=PIPE)
            if p.stderr.read():
                self.error('Problem syncing filesystem. Please run the sync command.')

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
            ret = ord(self.call_sg_raw('get_setting', 'needs_repair', 1))
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

    def mount(self):
        try:
            self.call_sg_raw('unlock')
        except Exception, e:
            self.rerror(e)
   


    def eject(self):
        try:
            self.sync()
            self.call_sg_raw('disconnect')
        except Exception, e:
            self.rerror(e)



    def upload_firmware(self, lpath):
        try:
            fw = fwdidj.config(self, self._mount_config.host_id, 'firmware')
            paths = fw.prepare_update(lpath) 
            self.move_update(paths)
        except Exception, e:
            self.rerror(e)



    def upload_bootloader(self, lpath):
        try:
            fw = fwdidj.config(self, self._mount_config.host_id, 'bootloader')
            paths = fw.prepare_update(lpath)           
            self.move_update(paths)
        except Exception, e:
            self.rerror(e)



    def cleanup(self):
        try:
            fwpath = os.path.join(self._mount_config.host_id, fwdidj.DIDJ_REMOTE_FW_DIR)
            blpath = os.path.join(self._mount_config.host_id, fwdidj.DIDJ_REMOTE_BL_DIR)
                
            if os.path.exists(fwpath):            
                if not self._dbg.remove(fwpath):
                    rmtree(fwpath)
                
            if os.path.exists(blpath):            
                if not self._dbg.remove(fwpath):
                    rmtree(blpath)

        except Exception, e:
            self.rerror(e)
