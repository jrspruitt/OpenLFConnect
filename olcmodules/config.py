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