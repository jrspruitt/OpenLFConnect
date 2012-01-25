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
# Version: Version 0.5
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
import os
import tarfile
import zipfile

def rename_lx_firmware(path):
    lx_fw_files_prefixs = {'first':'1048576,8,', 'kernel':'2097152,64,', 'erootfs':'10485760,688,'}
    dir_list = os.listdir(path)    

    for name, prefix in lx_fw_files_prefixs.iteritems():
        file_name_arr = [f for f in dir_list if name in f.lower() and not f.startswith(prefix)]
        for file_name in file_name_arr:
            file_path = os.path.join(path, file_name)
            new_path = os.path.join(path, '%s%s' % (prefix, file_name))
            if not os.path.exists(new_path) and os.path.exists(file_path):
                os.rename(file_path, new_path)
                print 'Renamed %s to %s' % (file_name, os.path.basename(new_path))


def extract_packages(path):
    exts = ('lfp','lf2')
    files = []
    if os.path.isdir(path):
        dir_list = os.listdir(path)
        files = [f for f in dir_list if f.endswith(exts)]
    else:
        if path.endswith(exts):
            path = os.path.dirname(path)
            files = [os.path.basename(path)]
    
    if len(files) > 0:
        for file_name in files:
            file_path = os.path.join(path, file_name)
            
            if file_name.endswith('lfp'):
                print 'Extracting lfp: %s' % file_name
                opener, mode = zipfile.ZipFile, 'r'
            elif file_name.endswith('lf2'):
                print 'Extracting lf2: %s' % file_name
                opener, mode = tarfile.open, 'r:bz2'
            else:
                assert False, 'Extracting error.'
            
            f = opener(file_path, mode)
            f.extractall(path)
            f.close() 
    else:
        assert False, 'No packages found.'



