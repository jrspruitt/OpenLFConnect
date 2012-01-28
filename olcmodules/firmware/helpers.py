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
# firmware.helpers.py Version 0.1

import os
from hashlib import md5, sha1


def error(e):
    assert False, '%s' % e



def get_md5(path):
    try:
        f = open(path, 'rb')
        md5h = md5()
        md5h.update(f.read())
        f.close()
        return md5h.hexdigest()
    except Exception, e:
        error(e)



def get_sha1(path):
    try:
        f = open(path, 'rb')
        sha1h = sha1()
        sha1h.update(f.read())
        f.close()
        return sha1h.hexdigest()
    except Exception, e:
        error(e)



def device_info(name):
    _lx_dir = os.path.abspath('files/Explorer')
    _lpad_dir = os.path.abspath('files/LeapPad')
    _didj_dir = os.path.abspath('files/Didj')
    
    _device_dir = {'Explorer':_lx_dir, 'LeapPad':_lpad_dir, 'Didj':_didj_dir}
    
    lpad_names = ['lpad', 'lxp', 'leappad', 'leappad explorer', 'explorer leappad']
    lx_names = ['lx', 'explorer', 'leapster explorer']
    didj_names = ['didj']

    if name.lower() in lpad_names:
        nname = 'LeapPad'
    elif name.lower() in lx_names:
        nname = 'Explorer'
    elif name.lower() in didj_names:
        nname = 'Didj'
    else:
        error('Device name could not be determined.')
    
    return [nname, _device_dir[nname]]



def wheres_firmware_dir(lpath, utype):
    if lpath[-1:] == '/':
        lpath = lpath[0:-1]

    if not os.path.basename(lpath) == utype:
        lpath = os.path.join(lpath, utype)
        
        if not os.path.exists(lpath) or not os.path.isdir(lpath):
            return False
            
    return lpath

