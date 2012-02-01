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
# config.py Version 0.1

import os
from shutil import copytree

FILES_DIR = 'files'

LPAD_NAME = 'Lpad'
LPAD_NAMES = ['lpad', 'lxp', 'leappad', 'leappad explorer', 'explorer leappad']
LPAD_VDICT = 'leappadexplorer'
LPAD_DIR = os.path.abspath(os.path.join(FILES_DIR, LPAD_NAME))

LX_NAME = 'LX'
LX_NAMES = ['lx', 'explorer', 'leapster explorer']
LX_VDICT = 'lexplorer'
LX_DIR = os.path.abspath(os.path.join(FILES_DIR, LX_NAME))

DIDJ_NAME = 'Didj'
DIDJ_NAMES = ['didj']
DIDJ_VDICT = 'didj'
DIDJ_DIR = os.path.abspath(os.path.join(FILES_DIR, DIDJ_NAME))

DOWNLOAD_NAME = 'Downloads'
DOWNLOAD_DIR = os.path.abspath(os.path.join(FILES_DIR, DOWNLOAD_NAME))

SCRIPTS_NAME = 'Scripts'
SCRIPTS_DIR = os.path.abspath(os.path.join(FILES_DIR, SCRIPTS_NAME))



def error(e):
    assert False, '%s' % e



def olc_files_dirs_check():
    try:
        dirs = [LPAD_DIR, LX_DIR, DIDJ_DIR, DOWNLOAD_DIR, SCRIPTS_DIR]
        
        for item in dirs:
                
            if not os.path.exists(item):
                if item == SCRIPTS_DIR:
                    copytree('extras/dftp_scripts', SCRIPTS_DIR)
                else:
                    os.mkdir(item)
                
                print 'Created %s/%s/' % (os.path.basename(os.path.dirname(item)), os.path.basename(item))
            elif not os.path.isdir(item):
                error('Name conflict in files directory.')
    except Exception, e:
        error(e)



def olc_device_settings(name):
    if name.lower() in LPAD_NAMES:
        nname = LPAD_NAME
        vdict = LPAD_VDICT
        fdir = LPAD_DIR
    elif name.lower() in LX_NAMES:
        nname = LX_NAME
        vdict = LX_VDICT
        fdir = LX_DIR
    elif name.lower() in DIDJ_NAMES:
        nname = DIDJ_NAME
        vdict = DIDJ_VDICT
        fdir = DIDJ_DIR
    else:
        error('Device name could not be determined.')
    
    return {'name':nname, 'dir':fdir, 'vdict':vdict}



class debug(object):
    def __init__(self, module):
        self.module = module


    def wrapper(self, debug):
        if self.module.debug:
            print '-----------------'
            print debug
            print '\n'
            return True
        else:
            return False
    
    
    
    def make(self, path):
        debug = 'Made: %s' % os.path.basename(path)
        return self.wrapper(debug)
    
    
    
    def upload(self, lpath, rpath):
        debug = """
    local: %s
    remote: %s
            """ % (lpath, rpath)
        return self.wrapper(debug)
    
    
    
    def download(self, lpath, rpath):
        debug = """
    local: %s
    remote: %s
            """ % (lpath, rpath)
        return self.wrapper(debug)
    
    
    
    def remove(self, path):
        debug = 'Deleted: %s' % os.path.basename(path)
        return self.wrapper(debug)
    
    

    def run_script(self, path):
        debug = 'Ran Script: %s' % os.path.basename(path)
        return self.wrapper(debug)