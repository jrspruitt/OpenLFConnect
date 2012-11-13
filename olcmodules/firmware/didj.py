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
# firmware.didj.py Version 0.2.2

import os
from olcmodules.firmware.hash import get_md5
from olcmodules.config import debug as dbg

DIDJ_FW_DIR = 'firmware-LF_LF1000'
DIDJ_REMOTE_FW_DIR = os.path.join('Base/', DIDJ_FW_DIR)
DIDJ_FW_FILES = ['erootfs','kernel']
DIDJ_REMOTE_FW_FILES = {'erootfs':'erootfs.jffs2','kernel':'kernel.bin'}



DIDJ_BL_DIR = 'bootstrap-LF_LF1000'
DIDJ_REMOTE_BL_DIR = os.path.join('Base/', DIDJ_BL_DIR)
DIDJ_BL_FILES = ['lightning-boot']
DIDJ_REMOTE_BL_FILES = {'lightning-boot':'lightning-boot.bin'}



class config(object):
    def __init__(self, module, mount_point, utype=''):
        self._utype = utype
        self._dbg = dbg(module)
        
        if self._utype == 'firmware':
            self._remote_fw_files = DIDJ_REMOTE_FW_FILES
            self._fw_dir = DIDJ_FW_DIR
            self._remote_fw_dir = os.path.join(mount_point, DIDJ_REMOTE_FW_DIR)
            self._fw_files = DIDJ_FW_FILES

        elif self._utype == 'bootloader':
            self._remote_fw_files = DIDJ_REMOTE_BL_FILES
            self._fw_dir = DIDJ_BL_DIR
            self._remote_fw_dir = os.path.join(mount_point, DIDJ_REMOTE_BL_DIR,)
            self._fw_files = DIDJ_BL_FILES
        else:
            self.error('No update type selected.')

        self._fw_file_counter = list(self._fw_files)



    def error(self, e):
        assert False, e



    def didj_md5_file(self, path, file_name):
        try:
            if os.path.exists(path):
                md5sum = get_md5(path)
                md5_path = os.path.join(os.path.dirname(path), '%s.md5' % os.path.splitext(file_name)[0])
                if not self._dbg.make(md5_path):
                    f = open(md5_path, 'w')
                    f.write(md5sum)
                    f.close
                else:
                    print md5sum
                return md5_path
        except Exception, e:
            self.error(e)
    
    
    
    def get_file_paths(self, lpath):
        try:
            file_name = os.path.basename(lpath)
            lfile_path = None
            rfile_path = None
            file_list = []
            for base_name in self._fw_files:
                if base_name in file_name and not file_name.endswith('md5'):
                    del self._fw_file_counter[self._fw_file_counter.index(base_name)]
                    lfile_path = lpath
                    rfile_path = os.path.join(self._remote_fw_dir, self._remote_fw_files[base_name])
                    md5_lpath = self.didj_md5_file(lfile_path, file_name)
                    file_list.append([lfile_path, rfile_path])
                    file_list.append([md5_lpath, '%s.md5' %os.path.splitext(rfile_path)[0]])

            if file_list:
                return file_list
            else:
                return False
        except Exception, e:
            self.error(e)
    
    
    
    def prepare_update(self, lpath):
        try:
            file_paths = []
            # firmware update
            if os.path.isdir(lpath):
                if lpath[-1:] == '/':
                    lpath = lpath[0:-1]
                
                check_fw_path = os.path.join(lpath, self._fw_dir)
                
                if os.path.exists(check_fw_path):
                    lpath = check_fw_path 
                
                for item in os.listdir(lpath):
                    paths = self.get_file_paths(os.path.join(lpath, item))
                    if paths:
                        file_paths.append(paths)
                        
            else:
                # This can only be lightning-boot
                if self._fw_files[0] in lpath:
                    paths = self.get_file_paths(lpath)
                    if paths:
                        file_paths.append(paths)
                    
            if self._fw_file_counter:
                self.error('Missing update file: %s' % ' '.join(self._fw_file_counter))

            if file_paths:
                if not os.path.exists(self._remote_fw_dir) and not self._dbg.make(self._remote_fw_dir):
                    os.mkdir(self._remote_fw_dir)                    

                return file_paths            
            else:
                self.error('No firmware files found.')
        except Exception, e:
            self.error(e)
        
        
