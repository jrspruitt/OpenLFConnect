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
# Version: Version 0.3
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform
##############################################################################

import os
import sys
import shlex
import shutil
import hashlib
import subprocess

class client(object):
    def __init__(self):
        self.debug = False
        self._didj_base = 'Base/'
        
        self._bootloader_dir = 'bootstrap-LF_LF1000'
        self._bootloader_files = ['lightning-boot.bin']
        
        self._firmware_dir = 'firmware-LF_LF1000'
        self._firmware_files = ['kernel.bin', 'erootfs.jffs2']
        
        self._cdb_cmds = {'lock':'C1', 'unlock':'C2', 'get_setting':'C3', 'disconnect':'C6'}
        self._settings = {'battery':'02', 'serial':'03', 'needs_repair':'06', '00':'00' }
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
                    md5 = hashlib.md5()
                    md5.update(f.read())
                    md5hash = md5.hexdigest()
                    f.close()
                    md5_file_name = os.path.splitext(os.path.basename(file_path))[0]
                    md5_file_path = os.path.join(lpath, '%s.md5' % md5_file_name)
                    f = open(md5_file_path, 'wb')
                    f.write(md5hash)
                    f.close
            return True
        except Exception, e:
            self.error(e)



    def call_sg_raw(self, cmd, dev_id, arg='00'):
        try:
                if len(self._settings[arg]) == 0:
                    self.error('Bad settings value')                    
                elif len(self._cdb_cmds[cmd]) == 0:
                    self.error('Bad command')

                cmdl = '%s %s %s %s 00 00 00 00 00 00 00 00' % (self._sg_raw, dev_id, self._cdb_cmds[cmd], self._settings[arg])
                cmd = shlex.split(cmdl)
                p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
                err = p.stderr.read()
                
                if err.find('Good') == -1:
                    self.error('SCSI error.')       
        except Exception, e:
            self.error(e)



    def get_update_paths(self, lpath, mpoint, type_dir):
        try:
            if lpath[-1:] == '/':
                lpath = lpath[0:-1]

            if not os.path.basename(lpath) == type_dir:
                if os.path.exists(os.path.join(lpath, type_dir)):
                    lpath = os.path.join(lpath, type_dir)
                else:
                    self.error('Firmware directory not found.')

            rpath = os.path.join(mpoint, self._didj_base)
            
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
                    shutil.copytree(lpath, rpath)
            else:
                self.error('One of the paths does not exist')
        except Exception, e:
            self.error(e)


  
#######################
# Didj functions
#######################
    
    def umount(self, dev_id):
        try:
            self.call_sg_raw('lock', dev_id)
        except Exception, e:
            self.rerror(e)



    def mount(self, dev_id):
        try:
            self.call_sg_raw('unlock', dev_id)
        except Exception, e:
            self.rerror(e)



    def eject(self, dev_id):
        try:
            self.call_sg_raw('disconnect', dev_id)
            if not sys.platform == 'win32':
                print 'Please eject the device from your system.'
        except Exception, e:
            self.rerror(e)



    def upload_firmware(self, lpath, mpoint):
        try:
            lpath, rpath = self.get_update_paths(lpath, mpoint, self._firmware_dir)
            self.md5_files(self._firmware_files, lpath)
            
            if os.path.exists(rpath):
                self.error('Found %s on device already.' % self._firmware_dir)
            self.move_update(lpath, rpath)
        except Exception, e:
            self.rerror(e)



    def upload_bootloader(self, lpath, mpoint):
        try:
            lpath, rpath = self.get_update_paths(lpath, mpoint, self._bootloader_dir)
            self.md5_files(self._bootloader_files, lpath)
            
            if os.path.exists(rpath):
                self.error('Found %s on device already.' % self._bootloader_dir)
            self.move_update(lpath, rpath)
        except Exception, e:
            self.rerror(e)


    def cleanup(self, mpoint):
        try:
            rpath = os.path.join(mpoint, self._didj_base)
            
            if not os.path.exists(rpath):
                self.error('Could not find Base/ path on device.')
            else:
                fwpath = os.path.join(rpath, self._firmware_dir)
                blpath = os.path.join(rpath, self._bootloader_dir)
                
                if os.path.exists(fwpath):
                    shutil.rmtree(fwpath)
                    
                if os.path.exists(blpath):
                    shutil.rmtree(blpath)               
        except Exception, e:
            self.rerror(e)
