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
# firmware.dftp.py Version 0.3.0

import os
import ConfigParser
from olcmodules.firmware.cbf import check as cbf_check
from olcmodules.config import PARTITIONS_PATH

FUSE_FW_DIR = 'firmware'
FUSE_REMOTE_FW_ROOT = '/LF/fuse/'
FUSE_REMOTE_FW_DIR = os.path.join(FUSE_REMOTE_FW_ROOT, FUSE_FW_DIR)

DFTP_FW_DIR = 'Firmware-Base'
DFTP_REMOTE_FW_ROOT = '/LF/Bulk/Downloads/'
DFTP_REMOTE_FW_DIR = os.path.join(DFTP_REMOTE_FW_ROOT, DFTP_FW_DIR)

PACKET_SIZE = 131072


class config(object):
    def __init__(self, module, utype, config):
        self._module = module
        self._utype = utype
        
        self._remote_fw_files = ''
        self._fw_dir = ''
        self._remote_fw_dir = ''
        self._fw_files = ''
        self._cfg = ConfigParser.ConfigParser()
        self._cfg.read(os.path.join(PARTITIONS_PATH, config))
        self._remote_fw_files = {}
        self._fw_files = ()
        self.fs = ''
        self._set_fw()
 
    def _cfg_get_list(self):
            plist = self._cfg.get(self._utype, 'LIST')
            return plist.split(',')

    def _set_fw(self):
        plist = self._cfg_get_list()
        
        for part in plist:
            name = self._cfg.get(part, 'NAME')
            match = self._cfg.get(part, 'MATCH')

            if self._utype == 'dftp':
                addr = self._cfg.get(part, 'ADDR')
                size = self._cfg.get(part, 'SIZE')
                self.fs += '%s %s payload/%s\n' % (addr, size, name)
                name = '%s,%s,%s' % (eval(addr), (eval(size)/PACKET_SIZE), name)
                
            self._fw_files += (match,)
            self._remote_fw_files[match] = name

        if self._utype == 'fuse':
            self._fw_dir = FUSE_FW_DIR
            self._remote_fw_dir = FUSE_REMOTE_FW_DIR

        elif self._utype == 'dftp':
            self._fw_dir = DFTP_FW_DIR
            self._remote_fw_dir = DFTP_REMOTE_FW_DIR
        else:
            self.error('No update type selected.')



    def error(self, e):
        assert False, e
    
 
    def get_file_paths(self, lpath):
        try:
            dir_list = []

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
                    if base_name in base_file_name:
                        rpath = os.path.join(self._remote_fw_dir, self._remote_fw_files[base_name])
                        file_paths = [[lpath, rpath]]
                        break     

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
                self.error('No firmware files found.')
        except Exception, e:
            self.error(e)
        
        
        
