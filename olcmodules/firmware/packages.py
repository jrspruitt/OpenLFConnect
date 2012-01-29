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
# firmware.packages.py Version 0.1

import os
import tarfile
import zipfile
import xml.dom.minidom as xml
from urllib import urlretrieve
from urllib2 import urlopen

from olcmodules.firmware.helpers import get_sha1, device_info

lpad_firmware_guid = ['LPAD-0x001E0012-000001', 'LPAD-0x001E0012-000003']
lpad_surgeon_guid = ['LPAD-0x001E0011-000000']

lx_firmware_guid = ['LST3-0x00170029-000000']
lx_surgeon_guid = ['LST3-0x00170028-000000']

didj_firmware_guid = ['DIDJ-0x000E0003-000001']
didj_bootloader_guid = ['DIDJ-0x000E0002-000001']



def error(e):
    assert False, '%s' % e



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
                error('Extracting error.')
            
            f = opener(file_path, mode)
            f.extractall(path)
            f.close() 
    else:
        error('No packages found.')



class lf_packages(object):
    def __init__(self):
        self._lpad_guids = {'firmware':lpad_firmware_guid, 'surgeon':lpad_surgeon_guid}
        self._lx_guids = {'firmware':lx_firmware_guid, 'surgeon':lx_surgeon_guid}
        self._didj_guids = {'firmware':didj_firmware_guid, 'bootloader':didj_bootloader_guid}
        self._guid_list = {'LeapPad':self._lpad_guids, 'Explorer':self._lx_guids, 'Didj':self._didj_guids}
        self._vdict_name = {'LeapPad':'leappadexplorer', 'Explorer':'lexplorer', 'Didj':'didj'}



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



    def _pname_normalizer(self, ptype):
        if 'firmware' in ptype.lower():
            ptype = 'firmware'
        elif 'surgeon' in ptype.lower():
            ptype = 'surgeon'
        elif 'bootloader' in ptype.lower():
            ptype = 'bootloader'
        else:
            error('Could not determine package you meant.')
        
        return ptype



    def _get_package_info(self, comps, guid):
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



    def get_package(self, dtype, ptype):
        dname, fwdir = device_info(dtype)
        ptype = self._pname_normalizer(ptype)
        
        dom = self._get_vdict_dom(self._vdict_name[dname])        
        urls = self._get_package_info(dom.getElementsByTagName('Component'), self._guid_list[dname][ptype])

        for pname, pver, purl, pchecksum in urls:             
            package_name = os.path.basename(purl)
            ext = os.path.splitext(package_name)[1]
            
            if dname == 'LeapPad':
                if 'Base' in pname:
                    ptype = '%s_%s' % (ptype, 'base')
                elif 'Partition' in pname:
                    ptype = '%s_%s' % (ptype, 'partition')

            file_name = '%s_%s_%s%s' % (dname, ptype, pver, ext)
            file_path = os.path.join(fwdir, file_name)
            
            if not os.path.exists(file_path):
                urlretrieve(purl, file_path)
                print 'Downloading: %s' % file_name
                sha1sum = get_sha1(file_path)

                if sha1sum == pchecksum:
                    print 'Packaged passed checksum'
                else:
                    error('Package failed checksum. Please check the file.')

            else:
                error('Package already exists.')




