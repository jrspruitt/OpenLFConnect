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

PACKET_SIZE = 131072


class config(object):
    def __init__(self, device_profile, lpath):
        self._device_profile = device_profile.get()
        self._lpath = lpath
        self._lpath_isdir = os.path.isdir(lpath)

        self._local_file_list = []
        self._fw_conf_info = []
        self._remote_fw_path = self._device_profile['firmware']['remote_path']        
        
        self.fs = ''

        self._checkset_fw_dirs()
        self._create_lfile_list()

 

    def error(self, e):
        assert False, e

        
    def _checkset_fw_dirs(self):
        if self._lpath_isdir:

            if self._lpath[-1:] == '/':
                self._lpath = self._lpath[0:-1]

            local_fw_name = self._device_profile['firmware']['local_dir']
                
            check_fw_path = os.path.join(self._lpath, local_fw_name)
            
            if os.path.exists(check_fw_path):
                self._lpath = check_fw_path


    def _create_lfile_list(self):
        if self._lpath_isdir:
            for file_name in os.listdir(self._lpath):
                file_path = os.path.join(self._lpath, file_name)

                if file_name == 'sd' and os.path.isdir(file_path):
                    for file_iname, file_info in self._device_profile['firmware']['file_info'].items():
                        sd_file_path = os.path.join(self._lpath, file_info['name'])

                        if os.path.exists(sd_file_path):
                                self._local_file_list.append(sd_file_path)
                else:
                    self._local_file_list.append(os.path.join(self._lpath, file_name))

        else:
            self._local_file_list.append(self._lpath)


    def get_file_paths(self):
        fw_files = []
        fw_names = self._device_profile['firmware']['names'].split(',')
        fw_version = int(self._device_profile['firmware']['version'])
        fw_file_count = len(fw_names)

        for fw_lfile in self._local_file_list:
            for file_name, file_info in self._device_profile['firmware']['file_info'].items():
                if file_info['match'] in fw_lfile:
                    fw_file_count -= 1

                    if fw_version == 1:
                        if 'addr' in file_info and 'size' in file_info:
                            self.fs += '%s %s payload/%s\n' % (file_info['addr'], file_info['size'], name)
                            file_rname = '%s,%s,%s' % (eval(file_info['addr']), (eval(file_info['size'])/PACKET_SIZE), name)
                        else:
                            file_rname = file_info['name']

                    elif fw_version == 2:
                        if 'part_num' in file_info:
                            file_size = os.path.getsize(fw_lfile)
                            name = '%s,%s,%s' % (file_info['part_num'], file_size, file_info['name'])
                        else:
                            file_rname = file_info['name']
                    else:
                        self.error('DFTP version \'%s\' is not supported.' % fw_version)

                    fw_files.append((fw_lfile, os.path.join(self._remote_fw_path, file_rname)))

            if fw_file_count == 1:
                break

        if fw_files:
            return fw_files
        else:
            self.error('No firmware files found.')
 



