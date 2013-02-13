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
# config.py Version 0.3

import os
from shutil import copytree

APP_PATH = os.path.dirname(os.path.dirname(__file__))
FILES_PATH = os.path.join(APP_PATH, 'files')

LPAD_NAME = 'Lpad'
LPAD_NAMES = ['lpad', 'lxp', 'leappad', 'leappad explorer', 'explorer leappad']
LPAD_VDICT = 'leappadexplorer'
LPAD_DCONT = 'LPAD'
LPAD_PATH = os.path.join(FILES_PATH, LPAD_NAME)

LX_NAME = 'LX'
LX_NAMES = ['lx', 'explorer', 'leapster explorer']
LX_VDICT = 'lexplorer'
LX_DCONT = 'LST3'
LX_PATH = os.path.join(FILES_PATH, LX_NAME)

DIDJ_NAME = 'Didj'
DIDJ_NAMES = ['didj']
DIDJ_VDICT = 'didj'
DIDJ_DCONT = ''
DIDJ_PATH = os.path.join(FILES_PATH, DIDJ_NAME)

LXGS_NAME = 'LXGS'
LXGS_NAMES = ['lxgs', 'gs', 'explorer gs']
LXGS_VDICT = ''
LXGS_DCONT = 'GAMFW'
LXGS_PATH = os.path.join(FILES_PATH, LXGS_NAME)

LPAD2_NAME = 'Lpad2'
LPAD2_NAMES = ['lpad2', 'lxp2', 'leappad2', 'leappad2 explorer', 'explorer leappad2']
LPAD2_VDICT = ''
LPAD2_DCONT = 'PADFW'
LPAD2_PATH = os.path.join(FILES_PATH, LPAD2_NAME)


DOWNLOAD_NAME = 'Downloads'
DOWNLOAD_PATH = os.path.abspath(os.path.join(FILES_PATH, DOWNLOAD_NAME))

EXTRAS_NAME = 'Extras'
EXTRAS_PATH = os.path.join(APP_PATH, FILES_PATH, EXTRAS_NAME)
SCRIPTS_NAME = 'Scripts'
SCRIPTS_PATH = os.path.join(EXTRAS_PATH, SCRIPTS_NAME)
PARTITIONS_NAME = 'Partitions'
PARTITIONS_PATH = os.path.join(EXTRAS_PATH, PARTITIONS_NAME)

def error(e):
    assert False, '%s' % e


def olc_files_dirs_check():
    try:

        if not os.path.exists(FILES_PATH):
            os.mkdir(FILES_PATH)
            print 'Files folder is missing, lets repopulate.'
            print 'Created %s/' % FILES_PATH

        dirs = [LPAD_PATH, LX_PATH, DIDJ_PATH, LXGS_PATH, LPAD2_PATH, DOWNLOAD_PATH, EXTRAS_PATH, SCRIPTS_PATH, PARTITIONS_PATH]

        for item in dirs:

            if not os.path.exists(item):
                if item == SCRIPTS_PATH:
                    copytree(os.path.join(APP_PATH, 'extras/dftp_scripts'), SCRIPTS_PATH)
                elif item == PARTITIONS_PATH:
                    copytree(os.path.join(APP_PATH, 'extras/dftp_partitions'), PARTITIONS_PATH)
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
        dcont = LPAD_DCONT
        fdir = LPAD_PATH
    elif name.lower() in LX_NAMES:
        nname = LX_NAME
        vdict = LX_VDICT
        dcont = LX_DCONT
        fdir = LX_PATH
    elif name.lower() in DIDJ_NAMES:
        nname = DIDJ_NAME
        vdict = DIDJ_VDICT
        dcont = DIDJ_DCONT
        fdir = DIDJ_PATH
    elif name.lower() in LXGS_NAMES:
        nname = LXGS_NAME
        vdict = LXGS_VDICT
        dcont = LXGS_DCONT
        fdir = LXGS_PATH
    elif name.lower() in LPAD2_NAMES:
        nname = LPAD2_NAME
        vdict = LPAD2_VDICT
        dcont = LPAD2_DCONT
        fdir = LPAD2_PATH
    else:
        error('Device name could not be determined.')
    
    return {'name':nname, 'dir':fdir, 'vdict':vdict, 'dcont':dcont}



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
