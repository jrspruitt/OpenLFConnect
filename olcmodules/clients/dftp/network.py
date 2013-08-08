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
# client/dftp/network.py Version 0.0.1

from time import sleep
import socket

class connection():
    def __init__(self, conn_iface):
       self._conn_iface = conn_iface
       self._sock0 = None
       self._sock1 = None
       self._recieve_timeout = 2

    def error(self, e):
        assert False, e

    def timeout(self, t=None):
        if t is None:
            t = self._recieve_timeout
        self._sock1.settimeout(t)

    def create_client(self):
        device_id = self._conn_iface.device_id
        host_id = self._conn_iface.host_id
        self._sock0 = self.create_socket(device_id, 5000)
        self._sock0.sendall('ETHR %s 1383\x00' % host_id)
        sleep(2)
        self._sock1 = self.create_socket(device_id, 5001)
        self._sock1.settimeout(self._recieve_timeout)
        self.receive() 

    def disconnect(self):
        self._sock0.close()
        self._sock0 = None
        self._sock1.close()
        self._sock1 = None

    def send(self, data, type='small'):
        try:
            return self._sock0.send(data)
        except Exception, e:
            self.error('Send error: %s' % e)



    def receive(self, type='small'):
        try:
            if type == 'small':
                size = 4096
            else:
                size = 8192
            
            return self._sock1.recv(size)     
        except socket.timeout:
            return False



    def sendrtn(self, cmd, array=False):
        try:
            if not self._sock0:
                self.error('Device not connected.')
                
            self.send('%s\x00' % cmd)
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



    def create_socket(self, device_ip, port):
        for info in socket.getaddrinfo(device_ip, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = info
            
            try:
                sock = socket.socket(af, socktype, proto)
            except socket.error, e:
                sock = None
                continue
            
            try:
                sock.connect(sa)
            except socket.error, e:
                sock.close()
                sock = None
                continue
            
        if sock is None:
            self.error('Could not create socket to: %s' % (device_ip))
        else:
            return sock


    def download_buffer(self, path):
        try:
            if self.sendrtn('RETR %s' % path.replace('\\', '/')):
                ret_buf = ''
                buf = ''
                error = False
                self.send('100 ACK: %s\x00' % 0)
                    
                while True:                    
                    buf = self.receive('large')
    
                    if buf is False:
                        continue                        
                    elif '101 EOF' in buf:
                        break
                    elif '500 unknown command' in buf.lower():
                        error = True
                        break
                    else:
                        self.send('100 ACK: %s\x00' % len(buf))
                        ret_buf += buf
                if error:
                    return False
                else:
                    return ret_buf
        except Exception, e:
            self.error(e)



    def upload_buffer(self, buf, rpath):
        try:
            if self.sendrtn('STOR %s' % rpath.replace('\\', '/')):             
                bytes_sent = self.send(buf)
                ret = True
                    
                while ret:
                    ret = self.receive()
                        
                    if ret and '500 Unknown command' in ret:
                        self.error('Problem occured while uploading.')
                        
                self.sendrtn('101 EOF')
                return bytes_sent
            else:
                self.error('Failed to uDIRpload file.')
        except Exception, e:
            self.error(e)



    def run_buffer(self, buf):
        try:
            if not buf.startswith('#!/bin/sh'):
                self.error('File does not appear to be valid shell script, missing shebag line.')
            
            if self.sendrtn('RUN'):             
                self.send(buf.replace('\r', ''))
                ret = True
                
                while ret:
                    ret = self.receive()
                    
                    if ret and '500 Unknown command' in ret:
                        self.error('Problem occured while uploading.') 
                
                self.sendrtn('101 EOF')
                running = True
                
                while running:
                    ret = self.sendrtn('GETS SCRIPT_RUNNING', True)
                    if 'SCRIPT_RUNNING=1' in ret[0] :
                        running = False

                return True
            else:
                self.error('Failed to run script.')
        except Exception, e:
            self.error(e)
