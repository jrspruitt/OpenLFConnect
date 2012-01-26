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
# packages.py Version 0.6
import os
import tarfile
import zipfile

def extract(path):

    exts = ('lfp','lf2')
    files = []
    if os.path.isdir(path):
        dir_list = os.listdir(path)
        files = [f for f in dir_list if f.endswith(exts)]
    else:
        if path.endswith(exts):
            files = [os.path.basename(path)]
            path = os.path.dirname(path)
    
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