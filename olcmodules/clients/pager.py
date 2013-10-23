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
# pager.py Version 0.7
import os
import sys
import struct
from shlex import split as shlex_split
from subprocess import Popen, PIPE

from olcmodules.firmware import cbf

class client(object):
    def __init__(self, mount_config, debug=False):
        self.debug = debug
        self._mount_config = mount_config
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

#######################
# User functions
#######################

    def upload(self, path):
        try:
            if not os.path.exists(path) or os.path.isdir(path):
                self.error('Surgeon not found.')
                    
            cbf.check(path)
            buf = ''
            with open(path, 'rb') as f:
                buf = f.read()
                f.close()

            buf_len = len(buf)

            packet_leftovers = buf_len % cbf.PACKET_SIZE
            if packet_leftovers > 0:
                padding_size = cbf.PACKET_SIZE - packet_leftovers
                buf += struct.pack('%ss' % padding_size, '\xFF'*padding_size)

            buf_len = len(buf)
            packets = buf_len/cbf.PACKET_SIZE

            byte1 = '00'
            total = 0
            last_total = 0

            for i in range(0, packets):
                cmdl = '%s %s -b -s %s -n 2A 00 00 00 00 %s 00 00 20 00' % (self._sg_raw, self._mount_config.device_id, cbf.PACKET_SIZE, byte1)
                cmd = shlex_split(cmdl)
                byte1 = '01'
                p = Popen(cmd, stdin=PIPE, stderr=PIPE)
                p.stdin.write(buf[last_total:last_total+cbf.PACKET_SIZE])
                err = p.stderr.read()
                
                if not 'Good' in err:
                    self.error('SCSI error.')
                
                last_total += cbf.PACKET_SIZE

            p = Popen([self._sg_verify, self._mount_config.device_id], stderr=PIPE)
            err = p.stderr.read()
            
            if len(err) != 0:
                self.error('SCSI error.')                
        except Exception, e:
            self.rerror(e)


if __name__ == '__main__':
    print 'No examples yet.'
        




    
