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
# Version: Version 0.4
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform
##############################################################################

import sys
import re
import socket
import struct
import select
import netifaces as ni
from time import sleep
from shlex import split as shlex_split
from subprocess import Popen, PIPE

class connection(object):
    def __init__(self, host_ip='', device_ip='', debug=False):
        self.debug = debug
        self._conn_type = 'networking'
        self._root_dir = '/'
        
        self._host_ip = host_ip
        self._device_ip = device_ip
        self._subnet = '169.254.'
        self._host_ip_timeout = 120
        self._device_ip_timeout = 30

        self._m_ip = '224.0.0.251'
        self._m_port = 5002

        if sys.platform == 'win32':
            self._ping = 'ping -n 2 -w 500'
        else:
            self._ping = 'ping -c 2 -W 500'


#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Networking Error: %s' % e



    def multicast_listen_socket(self, m_ip, m_port):
        try:            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', m_port))
            mreq = struct.pack("4sl", socket.inet_aton(m_ip), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            return sock

        except socket.error, e:
            self.error('Multicast Socket: %s' % e)



    def set_windows_route(self):
        try:
            if sys.platform == 'win32' and self._device_ip and self._host_ip:
                child = Popen(['route.exe','ADD',self.device_ip, self.host_ip], stdout=PIPE, stderr=PIPE)
                err = child.stderr.read()
                
                if err:
                    self.error('Route could not be established.')
        except Exception, e:
            self.error(e)


    def get_net_interface(self, search_ip):
        ifs = ni.interfaces()
                    
        for intf in ifs:
            try:
                ip = ni.ifaddresses(intf)[2][0]['addr']
                if ip.startswith(search_ip):
                    return ip
            except:
                pass
        return False      



    def find_host_ip(self):
        print 'Finding Host IP'
        try:
            timeout = self._host_ip_timeout
            while timeout:
                
                ip = self.get_net_interface(self._subnet)
                if ip:
                    self._host_ip = ip
                    return ip
                sleep(1)
                timeout -= 1
                
            self.error('Timed out waiting for host IP.')
        except Exception, e:
            self.error(e)



    def find_device_ip(self):
        print 'Finding Device IP'
        try:
            sock = self.multicast_listen_socket(self._m_ip, self._m_port)
            rd, wd, xd = select.select([sock],[],[], self._device_ip_timeout)
    
            regx_IP = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)')
    
            if len(rd) != 0:
                socket_read = sock.recv(1024)
                m = regx_IP.search(socket_read)
                sock.close()
                
                if m:
                    self._device_ip = m.group('ip')
                    return self._device_ip
                else:
                    self.error('Couldn\'t get IP address.')
    
            else:
                self.error('Timed out waiting for device IP.')
        except Exception, e:
            self.error(e)
        
#######################
# Connection Interface Functions
#######################

    def get_conn_type_i(self):
        return self._conn_type


    def get_root_dir_i(self):
        return self._root_dir



    def get_device_id_i(self):
        return self._device_ip or self.find_device_ip()
    
    def set_device_id_i(self, ip):
        self._device_ip = ip
        self.set_windows_route()




    def get_host_id_i(self):
        return self._host_ip or self.find_host_ip()

    def set_host_id_i(self, ip):
        self._host_ip = ip
        self.set_windows_route()



    def is_connected_i(self):
        try:
            return self.get_net_interface(self._host_ip)
        except Exception, e:
            self.error(e)



    def ip_check(self, ip):
        pass
        #check conforms to ip
        #throw exceptions



    def device_check(self, ip):
        self.ip_check(ip)
        
    def host_check(self, ip):
        self.ip_check(ip)

if __name__ == '__main__':
    print 'No example yet'
