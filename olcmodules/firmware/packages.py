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
# firmware.packages.py Version 0.3

import os
import tarfile
import zipfile
import xml.dom.minidom as xml
from urllib import urlretrieve
from urllib2 import urlopen

from olcmodules import config
from olcmodules.firmware.hash import get_sha1

LPAD_FIRMWARE_GUID = ['LPAD-0x001E0012-000001', 'LPAD-0x001E0012-000003']
LPAD_SURGEON_GUID = ['LPAD-0x001E0011-000000']
LPAD_BULK_ERASE_GUID = ['LPAD-0x001E0012-000004']
LPAD_PTYPES = ['firmware', 'surgeon', 'bulk']
LPAD_GUIDS = {'firmware':LPAD_FIRMWARE_GUID, 'surgeon':LPAD_SURGEON_GUID, 'bulk':LPAD_BULK_ERASE_GUID}

LX_FIRMWARE_GUID = ['LST3-0x00170029-000000']
LX_SURGEON_GUID = ['LST3-0x00170028-000000']
LX_BULK_ERASE_GUID = ['LST3-0x00170037-000000']
LX_PTYPES = ['firmware', 'surgeon', 'bulk']
LX_GUIDS = {'firmware':LX_FIRMWARE_GUID, 'surgeon':LX_SURGEON_GUID, 'bulk':LX_BULK_ERASE_GUID}

DIDJ_FIRMWARE_GUID = ['DIDJ-0x000E0003-000001']
DIDJ_BOOTLOADER_GUID = ['DIDJ-0x000E0002-000001']
DIDJ_PTYPES = ['firmware', 'bootloader']
DIDJ_GUIDS = {'firmware':DIDJ_FIRMWARE_GUID, 'bootloader':DIDJ_BOOTLOADER_GUID}

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
    def __init__(self):
        self._guid_list = {config.LPAD_NAME:LPAD_GUIDS, config.LX_NAME:LX_GUIDS, config.DIDJ_NAME:DIDJ_GUIDS}



    def error(self, e):
        assert False, '%s' % e



    def _get_vdict_dom(self, vdict_name):
        try:
            vdict_url = 'http://lfccontent.leapfrog.com/%s/downloads/versionDictionary.xml' % vdict_name
            f = urlopen(vdict_url)
            vdict_xml = f.read().replace('\x92', '')
            dom = xml.parseString(vdict_xml)
            f.close()
            return dom
        except Exception, e:
            self.error(e)



    def _xml_get_text(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)



    def _input_check(self, dtype, ptype):
        if config.LPAD_NAME == dtype:
            fw_list = LPAD_PTYPES
        if config.LX_NAME == dtype:
            fw_list = LX_PTYPES
        if config.DIDJ_NAME == dtype:
            fw_list = DIDJ_PTYPES
            
        ptype = ptype.lower()

        if ptype in fw_list:
            return ptype
        else:
            error('Package specified is not available.')
        
            



    def _get_package_info(self, olc_ds, ptype):
        dom = self._get_vdict_dom(olc_ds['vdict'])
        comps = dom.getElementsByTagName('Component')
        guid = self._guid_list[olc_ds['name']][ptype]
        url_list = []

        for comp in comps:
            cguid = self._xml_get_text(comp.getElementsByTagName('Guid')[0].childNodes)

            if cguid in guid:
                del guid[guid.index(cguid)]
                name = self._xml_get_text(comp.getElementsByTagName('Name')[0].childNodes)
                ver = self._xml_get_text(comp.getElementsByTagName('Version')[0].childNodes)
                url = self._xml_get_text(comp.getElementsByTagName('Url')[0].childNodes)
                checksum = self._xml_get_text(comp.getElementsByTagName('Checksum')[0].childNodes)
                url_list.append((name, ver, url, checksum))
                if len(guid) < 1:
                    break
        return url_list



    def get_package(self, dtype, ptype, path):
        olc_ds = config.olc_device_settings(dtype)
        ptype = self._input_check(olc_ds['name'], ptype)
                
        urls = self._get_package_info(olc_ds, ptype)

        for pname, pver, purl, pchecksum in urls:             
            package_name = os.path.basename(purl)
            ext = os.path.splitext(package_name)[1]
            ptype_name = ptype

            if olc_ds['name'] == config.LPAD_NAME:
                if 'Base' in pname:
                    ptype_name = '%s_%s' % (ptype, 'base')
                elif 'Partition' in pname:
                    print ptype
                    ptype_name = '%s_%s' % (ptype, 'partition')

            file_name = '%s_%s_%s%s' % (olc_ds['name'], ptype_name, pver, ext)
            file_path = os.path.join(path, file_name)
            
            if not os.path.exists(file_path):
                urlretrieve(purl, file_path)
                print 'Downloading: %s' % file_name
                sha1sum = get_sha1(file_path)
                
                if sha1sum == pchecksum:
                    print 'Packaged passed checksum'
                else:
                    print 'Package failed checksum. Please check the file.'

            else:
                error('Package already exists.')




