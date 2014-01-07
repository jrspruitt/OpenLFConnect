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
# firmware.packages.py Version 0.4

import os
import tarfile
import zipfile
from copy import copy
import xml.dom.minidom as xml
from urllib import urlretrieve
from urllib2 import urlopen

from olcmodules import config

EXTS = ('lfp','lf2')

def error(e):
    assert False, '%s' % e


def extract(path):
    try:
        files = []
        if os.path.isdir(path):
            dir_list = os.listdir(path)
            files = [f for f in dir_list if f.endswith(EXTS)]
        else:
            if path.endswith(EXTS):
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
                    error('Extracting error.')
                
                f = opener(file_path, mode)
                f.extractall(path)
                f.close() 
        else:
            error('No packages found.')
    except Exception, e:
        error(e)



class lf_packages(object):
    def __init__(self, device_profile):
        self._package_types = ['bootloader','firmware','bulk','surgeon']
        self._device_profile = device_profile.get
        self._package_url_name = self._device_profile['names']['lf_url']
        if self._device_profile['firmware']['dftp_version'] < 2:
            self._url = 'http://lfccontent.leapfrog.com/%s/downloads/packages/%s'
        elif self._device_profile['firmware']['dftp_version'] == 2:
            self._url = 'http://digitalcontent.leapfrog.com/packages/%s/%s'
        else:
            self._url = ''

    def error(self, e):
        assert False, 'Packages: %s' % e


 
    def get_package(self, ptype, path):
        try:
            try:
                test = self._device_profile['names']['lf_url']
            except Exception, e:
                raise Exception('Packages not available for this profile.')

            if self._url == '':
                self.error('URL could not be determined. Check device profile.')

            ptype = ptype.lower()
            
            if ptype not in self._device_profile['packages']:
                self.error('Package type wrong for this device profile.')
            packages = self._device_profile['packages'][ptype].split(',')
            for package in packages:
                package_url = self._url % (self._package_url_name, package)
                package_lpath = os.path.join(path, package)
                if not os.path.exists(package_lpath):
                    urlretrieve(package_url, package_lpath)
                    print 'Downloading: %s' % package
    
                else:
                    print 'Package %s already exists.' % package
        except Exception, e:
            self.error(e)



