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
# lx.py Version 0.6
import os

def error(e):
    assert False, e

def check(path):
    # checks if directory has files ready to upload
    # false if needs formating
    pass

def rename(path):
    try:
        if not os.path.isdir(path):
            error('Path is not a directory.')

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
    except Exception, e:
        error(e)





