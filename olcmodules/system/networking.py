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
# networking.py Version 0.5
import sys
import re
import socket
import struct
import select
from time import sleep
from subprocess import Popen, PIPE

class connection(object):
    def __init__(self, host_ip='', device_ip='', debug=False):
        self.debug = debug
        
        self._root_dir = '/'

        self._subnet = '169.254.'
        self._host_ip_timeout = 120
        self._device_ip_timeout = 30

        self._m_ip = '224.0.0.251'
        self._m_port = 5002
        
        if sys.platform == 'win32':
            self._ifconfig = ['ipconfig', '/all']
        else:
            self._ifconfig = ['/sbin/ifconfig']
        
        if host_ip !='':
            if self.ip_check(host_ip):
                self._host_ip = host_ip
            else:
                self.rerror('Malformed host IP address.')
        else:
            self._host_ip = host_ip
            
        if device_ip != '':
            if self.ip_check(device_ip):
                self._device_ip = device_ip
            else:
                self.rerror('Malformed device IP address.')
        else:
            self._device_ip = device_ip

#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Networking Error: %s' % e



    def ip_check(self, ip):
        try:
            if ip.endswith('.'):
                ip = ip[0:-1]
                
            ip_arr = [int(ip_class) for ip_class in ip.split('.')]

            for ip_class in ip_arr:
                if not ip_class < 256 or not ip_class > -1:
                    return False
                
            if len(ip_arr) == 4:
                regex_ip = re.compile(r'\d+\.\d+\.\d+\.\d+')
                if regex_ip.search(ip):
                    return True
            else:
                return False
        except Exception, e:
            return False



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
            if sys.platform == 'win32' and self.get_device_id_i() and self.get_host_id_i():
                p = Popen(['route.exe','ADD', self.get_device_id_i(), self.get_host_id_i()], stdout=PIPE, stderr=PIPE)
                err = p.stderr.read()
                
                if err:
                    self.error('Route could not be established.')
        except Exception, e:
            self.error(e)



    def parse_ifconfig(self, search_ip):
        try:
            ip_arr = search_ip.split('.')
            ip = ''

            for i in range(0, 3):
                if i < len(ip_arr)-1:
                    ip += '%s\\.' % ip_arr[i]
                else:
                    ip += '\\d+\\.'

            if len(ip_arr) == 4:
                ip += '%s' % ip_arr[3]
            else:
                ip += '\\d+'

            p = Popen(self._ifconfig, stdout=PIPE, stderr=PIPE)
            err = p.stderr.read()
            
            if err:
                self.error('Could not get network info.')
            stdout = p.stdout.read()
            regx_ip = re.compile(r'(?P<ip>%s)' % ip)
            m = regx_ip.search(stdout)
            if m:
                return m.group('ip')
        except Exception, e:
            self.error(e)   



    def find_host_ip(self):
        try:
            timeout = self._host_ip_timeout

            while timeout:
                
                ip = self.parse_ifconfig(self._subnet)
                if ip:
                    self._host_ip = ip
                    if sys.platform == 'win32':
                        self.set_windows_route()
                    return ip
                sleep(1)
                timeout -= 1
                
            self.error('Timed out waiting for host IP.')
        except Exception, e:
            self.error(e)



    def find_device_ip(self):
        try:
            sock = self.multicast_listen_socket(self._m_ip, self._m_port)
            rd, wd, xd = select.select([sock],[],[], self._device_ip_timeout)
    
            regx_ip = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)')
    
            if len(rd) != 0:
                socket_read = sock.recv(1024)
                m = regx_ip.search(socket_read)
                sock.close()
                
                if m:
                    self._device_ip = m.group('ip')
                    return self._device_ip
                else:
                    self.error('Couldn\'t get device IP address.')
    
            else:
                self.error('Timed out waiting for device IP.')
        except Exception, e:
            self.error(e)
     
#######################
# Connection Interface Functions
#######################

    def get_root_dir_i(self):
        return self._root_dir



    def get_device_id_i(self):
        return self._device_ip or self.find_device_ip()



    def get_host_id_i(self):
        return self._host_ip or self.find_host_ip()



    def is_connected_i(self):
        try:
            return self.parse_ifconfig(self._host_ip)
        except Exception, e:
            self.error(e)

if __name__ == '__main__':
    print 'No example yet'
