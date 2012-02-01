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
# firmware.dftp.py Version 0.1

import os
from olcmodules.firmware.cbf import check as cbf_check


FUSE_FW_DIR = 'firmware'
FUSE_REMOTE_FW_ROOT = '/LF/fuse/'
FUSE_REMOTE_FW_DIR = os.path.join(FUSE_REMOTE_FW_ROOT, FUSE_FW_DIR)
FUSE_FW_FILES = ('rfs', 'FIRST_Lpad', 'kernel', 'mbr2G')
FUSE_REMOTE_FW_FILES = {'rfs':'sd/ext4/3/rfs',
                         'FIRST_Lpad':'sd/raw/1/FIRST_Lpad.cbf',
                         'kernel':'sd/raw/2/kernel.cbf',
                         'mbr2G':'sd/partition/mbr2G.image'}


DFTP_FW_DIR = 'Firmware-Base'
DFTP_REMOTE_FW_ROOT = '/LF/Bulk/Downloads/'
DFTP_REMOTE_FW_DIR = os.path.join(DFTP_REMOTE_FW_ROOT, DFTP_FW_DIR)
DFTP_FW_FILES = ('FIRST', 'kernel', 'erootfs')
DFTP_REMOTE_FW_FILES = {'FIRST':'1048576,8,FIRST.32.rle',
                         'kernel':'2097152,64,kernel.cbf',
                         'erootfs':'10485760,688,erootfs.ubi'}



class config(object):
    def __init__(self, module, utype=''):
        self._module = module
        self._utype = utype

        if self._utype == 'fuse':
            self._remote_fw_files = FUSE_REMOTE_FW_FILES
            self._fw_dir = FUSE_FW_DIR
            self._remote_fw_dir = FUSE_REMOTE_FW_DIR
            self._fw_files = FUSE_FW_FILES

        elif self._utype == 'dftp':
            self._remote_fw_files = DFTP_REMOTE_FW_FILES
            self._fw_dir = DFTP_FW_DIR
            self._remote_fw_dir = DFTP_REMOTE_FW_DIR
            self._fw_files = DFTP_FW_FILES
        else:
            self.error('No update type selected.')



    def error(self, e):
        assert False, e
    
    
    
    def get_file_paths(self, lpath):
        try:
            dir_list = []
            
            # Catch standard formated files
            for item in self._remote_fw_files.iteritems():
                lfile_path = os.path.join(lpath, item[1])
                if os.path.exists(lfile_path):
                    rfile_path = os.path.join(self._remote_fw_dir, item[1])
                    dir_list.append([lfile_path, rfile_path])

            # Non-standard formated then.
            # Match against base names.
            if not dir_list:
                for item in os.listdir(lpath):
                    for base_name in self._fw_files:
                        if base_name in item:
                            lfile_path = os.path.join(lpath, item)
                            rfile_path = os.path.join(self._remote_fw_dir, self._remote_fw_files[base_name])
                            dir_list.append([lfile_path, rfile_path])

            return dir_list
        except Exception, e:
            self.error(e)
    
    
    
    def prepare_update(self, lpath):
        try:        
            file_paths = []
            if os.path.isdir(lpath):
                
                if lpath[-1:] == '/':
                    lpath = lpath[0:-1]
                
                check_fw_path = os.path.join(lpath, self._fw_dir)
                
                if os.path.exists(check_fw_path):
                    lpath = check_fw_path 

                file_paths = self.get_file_paths(lpath)

            else:
                file_name = os.path.basename(lpath)
                base_file_name = os.path.splitext(file_name)[0]

                for base_name in self._fw_files:
                    if base_name.lower() in base_file_name:
                        rpath = os.path.join(self._remote_fw_dir, self._remote_fw_files[base_name])
                        file_paths = [[lpath, rpath]]
                        break     
#######
            print file_paths
            if file_paths:
                for item in file_paths:
                    if item[0].endswith('cbf'):
                        cbfchk = cbf_check(item[0], True)

                        if not cbfchk:
                            self.error('%s failed CBF check' % os.path.basename(item[0]))

                if not self._module.exists_i(self._remote_fw_dir):
                    self._module.mkdir_i(self._remote_fw_dir)
        
                return file_paths
            
            else:
                self.error('Problem with firmware.')
        except Exception, e:
            self.error(e)
        
        
        