##!/usr/bin/env python
##############################################################################
#    OpenLFConnect verson 0.2
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

# OpenLFConnect version 0.2

import os
import subprocess
import sys
import shlex

class pager(object):
    def __init__(self):
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

    def upload_firmware(self, path, dev_id):
        try:
            if not os.path.exists(path) or os.path.isdir(path):
                self.error('Surgeon not found.')
                    
            self.check_cbf(path)
            packets = self._file_size/self._cbf_packet
            byte1 = '00'
            total = 0
            last_total = 0
            
            for i in range(0, packets-1):
                cmdl = '%s %s -b -s %s -n -k %s -i "%s" 2A 00 00 00 00 %s 00 00 20 00' % (self._sg_raw, dev_id, self._cbf_packet, last_total, path, byte1)
                cmd = shlex.split(cmdl)
                byte1 = '01'
                p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
                err = p.stderr.read()
                
                if err.find('Good') == -1:
                    self.error('SCSI error.')
                
                total = last_total + self._cbf_packet - 1
                last_total = total + 1

            p = subprocess.Popen([self._sg_verify, dev_id], stderr=subprocess.PIPE)
            err = p.stderr.read()
            
            if len(err) != 0:
                self.error('SCSI error.')                
        except Exception, e:
            self.rerror(e)


if __name__ == '__main__':
        u = pager()
        




    
