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
# Version: Version 0.5
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
import os
import sys
from shlex import split as shlex_split
from subprocess import Popen, PIPE

class client(object):
    def __init__(self, mount_config, debug=False):
        self.debug = debug
        self._mount_config = mount_config
        
        self._cbf_packet = 16384
        self._cbf_magic = '\xf0\xde\xbc\x9a'
        self._file_size = 0
        
        if sys.platform == 'win32':
            self._sg_raw = 'bin/sg_raw'
            self._sg_verify = 'bin/sg_verify'
        else:
            self._sg_raw = 'sg_raw'
            self._sg_verify = 'sg_verify'


#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Pager Error: %s' % e



    def check_cbf(self, path):
        try:
            if not os.path.exists(path):
                self.error('Firmware not found')
            else:    
                f = open(path, 'rb')
                self._file_size = len(f.read())
                f.seek(0)
                magic = f.read(4)
                f.close()
                
                if not str(self._file_size/self._cbf_packet).isdigit():
                    self.error('File is the wrong size, should be multiple of %s.' % self._cbf_packet)

                if magic != self._cbf_magic:
                    self.error('File failed CBF Magic Number check.')
                else:
                    return True
        except Exception, e:
            self.error(e)



#######################
# User functions
#######################

    def upload_firmware(self, path):
        try:
            if not os.path.exists(path) or os.path.isdir(path):
                self.error('Surgeon not found.')
                    
            self.check_cbf(path)
            packets = self._file_size/self._cbf_packet
            byte1 = '00'
            total = 0
            last_total = 0
            
            for i in range(0, packets-1):
                cmdl = '%s %s -b -s %s -n -k %s -i "%s" 2A 00 00 00 00 %s 00 00 20 00' % (self._sg_raw, self._mount_config.device_id, self._cbf_packet, last_total, path, byte1)
                cmd = shlex_split(cmdl)
                byte1 = '01'
                p = Popen(cmd, stderr=PIPE)
                err = p.stderr.read()
                
                if 'Good' in err:
                    self.error('SCSI error.')
                
                total = last_total + self._cbf_packet - 1
                last_total = total + 1

            p = Popen([self._sg_verify, self._mount_config.device_id], stderr=PIPE)
            err = p.stderr.read()
            
            if len(err) != 0:
                self.error('SCSI error.')                
        except Exception, e:
            self.rerror(e)


if __name__ == '__main__':
    print 'No examples yet.'
        




    
