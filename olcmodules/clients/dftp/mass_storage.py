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
# client/dftp/mass_storage.py Version 0.0.2

import sys
from time import sleep
from shlex import split as shlex_split
from subprocess import Popen, PIPE

class connection():
    def __init__(self, conn_iface):
        self._conn_iface = conn_iface
        self._request_large = 10240
        self._request_small = 512

        if sys.platform == 'win32':
            self._sg_raw = 'bin/sg_raw'
        else:
            self._sg_raw = 'sg_raw'


    def error(self, e):
        assert False, e

    def timeout(self, t=None):
        pass

    def create_client(self):
        self._conn_iface.device_id
        while self.send('INFO\x00'):
            if self.receive():
                sleep(1)
                break
        

    def disconnect(self):
        pass


    def send(self, data, type='small'):
        try:
            data_len = len(data)
            bytes_sent = 0
            if type == 'small':
                request_len = self._request_small
                trans_len = '01'
                lba = '20'
            else:
                request_len = self._request_large
                trans_len = '14'
                lba = '40'

            i = 0
            while bytes_sent != data_len:
                data_p = data[i:request_len+i]
                data_p_len = len(data_p)

                data_p += '\x00'*(request_len-data_p_len)

                scsi_cmd = '%s %s -b -s %s -n 2A 80 00 00 00 %s 00 00 %s 00' % (self._sg_raw, self._conn_iface.device_id, request_len, lba, trans_len)
                scsi_cmd = shlex_split(scsi_cmd)
                p = Popen(scsi_cmd, stdin=PIPE, stderr=PIPE)
                p.stdin.write(data_p)
                i += request_len
                bytes_sent = bytes_sent + data_p_len

                if type == 'upload':
                    ret = self.receive()

                    if '102 BUSY' in ret:
                        while '102 BUSY' in ret: 
                            ret = self.receive()
                            sleep(.1)
                        continue
                    #elif not '200 OK' in ret:
                        #continue
                    elif not '103 CONT' in ret:
                        break

            if type == 'upload':
                self.sendrtn('101 EOF:%s\x00' % str(request_len - data_p_len))

            return bytes_sent
        except Exception, e:
            self.error('Send error: %s' % e)



    def receive(self, type='small'):
        try:
            if type == 'small':
                request_len = self._request_small
                trans_len = '01'
                lba = '20'
            else:
                request_len = self._request_large
                trans_len = '14'
                lba = '40' 
    
            scsi_cmd = '%s %s -b -r %s -n 28 00 00 00 00 %s 00 00 %s 00' % (self._sg_raw, self._conn_iface.device_id, request_len, lba, trans_len)
            scsi_cmd = shlex_split(scsi_cmd)
            p = Popen(scsi_cmd, stdout=PIPE, stderr=PIPE)
            buf = ''
            p.stdout.flush()
           
            line = p.stdout.read(1)
            if line == '':
                return False
            else:
                buf = line

            while True:
                line = p.stdout.read()
                
                if line == '':
                    break
                elif '102 BUSY' in line:
                    sleep(.1)
                elif '200 OK' in line:
                    buf += line
                    break
                else:
                    buf += line

            return buf
        except Exception, e:
            self.error('Receiving error: %s' % e)



    def sendrtn(self, cmd, array=False):
        try:
            self.send('%s' % cmd)
            ret = self.receive()
            if ret:
                retarr = ret.split('\n')
            else:
                self.error('Receiving error.')
            ok = False
            
            for item in retarr:
                if '200 OK' in item:
                    del retarr[retarr.index(item)]
                    ok = True

            if len(retarr) != 0 and not array:
                return '\n'.join(retarr)
            elif len(retarr) != 0 and array:
                return retarr
            elif ok:
                return True
            else:
                return False
        except Exception, e:
            self.error(e)




    def download_buffer(self, path):
        try:
            self.send('RETR %s\x00' % path.replace('\\', '/'))
            cmd_ret = self.receive().replace('\x00', '')

            if '200 OK' in cmd_ret:
                ret_buf = ''
                buf = ''
                error = False
                    
                while True:                    
                    buf = self.receive('large')
                    if '500 unknown command' in buf.lower():
                        error = True
                        break
                    else:
                        ret_buf += buf

                    sbuf = self.receive()
                    if '101 EOF' in sbuf:
                        break
                    elif '103 CONT' in sbuf:
                        continue
                    else:
                        error = True
                        break

                if '200 OK:' in cmd_ret:
                    ret_size = int(cmd_ret.replace('200 OK:', ''))
                else:
                    ret_size = ret_buf.find('\x00')

                if len(ret_buf) >= ret_size:
                    ret_buf = ret_buf[0:ret_size]

                if error:
                    return False
                else:
                    return ret_buf
        except Exception, e:
            self.error(e)



    def upload_buffer(self, buf, rpath):
        try:
            if self.sendrtn('STOR %s\x00' % rpath.replace('\\', '/')):             
                bytes_sent = self.send(buf, 'upload')
                return bytes_sent
            else:
                self.error('Failed to upload file.')
        except Exception, e:
            self.error(e)



    def run_buffer(self, buf):
        try:
            if not buf.startswith('#!/bin/sh'):
                self.error('File does not appear to be valid shell script, missing shebag line.')
            
            if self.sendrtn('RUN\x00'):             
                self.send(buf.replace('\r', ''), 'upload')
                
                while 1:
                    ret = self.sendrtn('GETS SCRIPT_RUNNING\x00', True)
                    if 'SCRIPT_RUNNING=1' in ret[0] :
                        break

                return True
            else:
                self.error('Failed to run script.')
        except Exception, e:
            self.error(e)
