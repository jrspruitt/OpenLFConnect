#!/usr/bin/env python
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

import sys
import re
import socket
import struct
import select
import subprocess

class config(object):
	def __init__(self):
		self._host_ip = ''
		self._device_ip = ''
		self._time_out = 30

		self._m_ip = '224.0.0.251'
		self._m_port = 5002



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



	def set_windows_route(self, device_ip, host_ip):
		try:
			subprocess.call(['route.exe','ADD',device_ip, host_ip])
			return True
		except Exception, e:
			self.error('Windows Route: %s' % e)


#######################
# User functions
#######################
	def get_device_ip(self):
		return self._device_ip or self.error('Device not set.')

	def set_device_ip(self, ip):
		self._device_ip = ip

	device_ip = property(get_device_ip, set_device_ip)



	def get_host_ip(self):
		return self._host_ip or self.error('Host not set.')

	def set_host_ip(self, ip):
		self._host_ip = ip

	host_ip = property(get_host_ip, set_host_ip)



	def establish_ip(self):
		try:
			sock = self.multicast_listen_socket(self._m_ip, self._m_port)
			rd, wd, xd = select.select([sock],[],[],self._time_out)
	
			regx_IP = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)')
	
			if len(rd) != 0:
				socket_read = sock.recv(1024)
				m = regx_IP.search(socket_read)
				sock.close()
				
				if m:
					self.device_ip = m.group('ip')
					
					if sys.platform == 'win32':
						self.set_windows_route(self.device_ip, self.host_ip)
						
					return True
				else:
					self.error('Couldn\'t get IP address.')
	
			else:
				self.error('Timed out waiting for device.')
		except Exception, e:
			self.rerror(e)



if __name__ == '__main__':
	d = config()
	print d.retrieve_ip()
