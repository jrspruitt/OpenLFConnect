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
# firmware.fuse.py Version 0.1
import os
from olcmodules.firmware.helpers import wheres_firmware_dir

fw_dir = 'firmware'
fw_files = [['sd/ext4/3/', 'rfs'], ['sd/raw/1/', 'FIRST_Lpad.cbf'], ['sd/raw/2/', 'kernel.cbf'], ['sd/partition/', 'mbr2G.image']]

remote_fw_root = '/LF/fuse/'
remote_fw_dir = os.path.join(remote_fw_root, fw_dir)



def error(e):
    assert False, e



def get_paths(path):
    # check if firmware/ is in this directory, or if we're in it
    # firmware/ must start with firmware, but could be firmware-backup/ or what ever
    # check if sd/x/x/file exists for at least 1 file
    # if not, check if firmwares exist in this directory
    # cbf_check kernel
    # format rpaths, and return
    # or fail
    pass



def prepare_update(dftp, lpath):
    try:
        lpath = wheres_firmware_dir(lpath, fw_dir)
        
        if not lpath:
            error('Firmware path not found.')
            # assume for now we'll always find it
            # later change to look for files here
        rpath = remote_fw_dir
        
        if not dftp.exists_i(rpath):
            dftp.mkdir_i(rpath)
    
        paths = []
    
        for fpath, fitem in fw_files:
            lfile_path = os.path.join(lpath, fpath, fitem)
            rfile_path = os.path.join(rpath, fpath, fitem)
            if os.path.exists(lfile_path):
                paths.append([lfile_path, rfile_path])
            else:
                print 'Skipping %s' % fitem
        return paths
    except Exception, e:
        error(e)

