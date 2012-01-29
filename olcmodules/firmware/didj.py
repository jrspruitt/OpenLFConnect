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
# firmware.didj.py Version 0.1

import os
from olcmodules.firmware.helpers import get_md5, wheres_firmware_dir

bootloader_dir = 'bootstrap-LF_LF1000'
bootloader_files = ['lightning-boot.bin']
        
firmware_dir = 'firmware-LF_LF1000'
firmware_files = ['kernel.bin', 'erootfs.jffs2']

update_dirs = {'bootloader': bootloader_dir, 'firmware': firmware_dir}
update_files = {'bootloader': bootloader_files, 'firmware': firmware_files}
didj_base = 'Base'



def error(e):
    assert False, '%s' % e



def didj_md5_files(path, utype):
    try:
        for item in update_files[utype]:
            fpath = os.path.join(path, item)
            if os.path.exists(fpath):
                md5sum = get_md5(fpath)
                md5_path = os.path.join(path, '%s.md5' % os.path.splitext(item)[0])
                f = open(md5_path, 'w')
                f.write(md5sum)
                f.close
    except Exception, e:
        error(e)



def find_paths(lpath, mount_point, utype):
    try:
        if lpath != '':
            lpath = wheres_firmware_dir(lpath, update_dirs[utype])
        
            if not lpath:
                error('Firmware path not found.')
                # check for files in this dir, make folder and move them 

        rpath = os.path.join(mount_point, didj_base)
        
        if not os.path.exists(rpath):
            error('Could not find Base/ path on device.')
        else:
            rpath = os.path.join(rpath, update_dirs[utype])
            
        return [lpath, rpath]
    except Exception, e:
        error(e)



def prepare_update(lpath, mount_point, utype):
    try:
        lpath, rpath = find_paths(lpath, mount_point, utype)

        if os.path.exists(rpath):
            error('Found %s update on device already.' % utype)
            
        didj_md5_files(lpath, utype)
        return [lpath, rpath]
    except Exception, e:
        error(e)