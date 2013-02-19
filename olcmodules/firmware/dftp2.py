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
# firmware.dftp2.py Version 0.1.0

import os
import ConfigParser
from olcmodules.firmware.cbf import check as cbf_check
from olcmodules import config
from olcmodules.config import PROFILES_PATH

PACKET_SIZE = 131072


class config(object):
    def __init__(self, module, device_profile, lpath):
        self._module = module
        self._device_profile = device_profile
        self._lpath = lpath
        self._lpath_isdir = os.path.isdir(lpath)

        self._local_file_list = ()
        self._fw_conf_info = []
        self._remote_fw_path = self._device_profile['firmware']['remote_dir']        
        
        self.fs = ''

        self._checkset_fw_dirs()
        self._create_lfile_list()

 

    def error(self, e):
        assert False, e

        
    def _checkset_fw_dirs(self):
        if self._lpath_isdir:

            if self._lpath[-1:] == '/':
                self._lpath = self._lpath[0:-1]

            local_fw_name = self._device_profile['firmware']['local_dirs']
                
            check_fw_path = os.path.join(self._lpath, local_fw_name)
            
            if os.path.exists(check_fw_path):
                self._lpath = check_fw_path
                
        if not self._module.exists_i(self._remote_fw_dir):
            self._module.mkdir_i(self._remote_fw_dir)


    def _create_lfile_list(self):
        if self._lpath_isdir:
            for file_name in os.listdir(self._lpath):
                self._local_file_list.append(os.path.join(self._lpath, file_name))

        else:
            self._local_file_list.append(self._lpath)



    def get_file_names(self):
        fw_files = []
        fw_file_count = len(self._device_profile['firmware']['firmware_names'])
        for fw_lfile in self._local_file_list:
            for file_info in self._device_profile['firmware']['firmware_names']:
                # not going to work with leappad1 sd/blah/blah
                if file_info['match'] in fw_lfile:
                    fw_file_count += 1
                    if self._device_profile['firmware']['version'] == '1':
                        pass
                        # dftp1 style update
                        if 'addr' in file_info and 'size' in file_info:
                            self.fs += '%s %s payload/%s\n' % (file_info['addr'], file_info['size'], name)
                            name = '%s,%s,%s' % (eval(file_info['addr']), (eval(file_info['size'])/PACKET_SIZE), name)
                            # assume custom partitions, make and upload 1.2.0.0.fs
                        else:
                            pass
                            # normal dftp1 update
                    elif self._device_profile['firmware']['version'] == '2':
                        if 'part_num' in file_info:
                            file_size = os.path.getsize(fw_lfile)
                            name = '%s,%s,%s' % (file_info['part_num'], file_size, file_info['name'])
                            # everything but lpad1v2
                        else:
                            name = file_info['name']
        
                fw_files.append((fw_lfile, os.path.join(self._remote_fw_dir, name)))

            if fw_file_count == 0:
                break

        if fw_files:
            return fw_files
        else:
            self.error('No firmware files found.')
 



