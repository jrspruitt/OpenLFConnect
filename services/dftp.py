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
# Version: Version 0.3
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform
##############################################################################

import os
import socket
import time

class client(object):
    def __init__(self):
        self.debug = False
        
        self._sock0 = None
        self._sock1 = None
        
        self._lx_fw_dir = 'Firmware-Base'
        self._lpad_fw_dir = 'firmware'
        
        self._lx_fw_files = ['1048576,8,FIRST.32.rle', '2097152,64,kernel.cbf', '10485760,688,erootfs.ubi']
        self._lpad_fw_files = ['sd/ext4/3/rfs', 'sd/raw/1/FIRST_Lpad.cbf', 'sd/raw/2/kernel.cbf', 'sd/partition/mbr2G.image']
          
        self._lx_remote_fw_dir = os.path.join('/LF/Bulk/Downloads/', self._lx_fw_dir)
        self._lpad_remote_fw_dir = os.path.join('/LF/fuse/', self._lpad_fw_dir)
        
        self._dftp_version = 0
        self._surgeon_dftp_version = '1.12'
        self._version_number = 0

#######################
# Internal functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'Dftp Error: %s' % e

    
    
    def create_socket(self, device, port):
        for serv_info in socket.getaddrinfo(device, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = serv_info
        
            try:
                sock = socket.socket(af, socktype, proto)
            except socket.error, msg:
                sock = None
                continue
                
            try:
                sock.connect(sa)
            except socket.error, msg:
                sock.close()
                sock = None
                continue
                
        if sock is None:
            self.error('Could not create socket')
        else:
            return sock



    def send(self, cmd):
        try:
            return self._sock0.send(cmd)
        except Exception, e:
            self.error('Send error: %s' % e)



    def receive(self, size=4096):
        try:
            return self._sock1.recv(size)     
        except socket.timeout:
            return False



    def sendrtn(self, cmd, array=False):
        try:
            if not self._sock0:
                self.error('Device not connected.')
                
            self.send('%s\x00' % cmd)
            ret = self.receive()
            retarr = ret.split('\n')
            ok = False
            
            for item in retarr:

                if item.find('200 OK') != -1:
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



    def exists(self, path):
        try:
            ret = self.sendrtn('LIST %s' % path)
    
            if ret.startswith('550'):
                self.error('Path does not exist.')
            else:
                return True
        except Exception, e:
            self.error(e)



    def get_version(self):
        try:
            lpath = os.path.abspath('files')
            loc_version = os.path.join(lpath, 'version')
            self.download_file(loc_version, '/etc/version')
            f = open(loc_version, 'rb')
            buf = f.readline()
            f.close()
            os.remove(loc_version)
            num = buf.strip()

            if len(num):
                return num
            else:
                return 0
        except Exception, e:
            self.error(e)




    def find_dftp_version(self):
        try:
            ret = self.sendrtn('INFO', True)
            
            for line in ret:
                if line.find('VERSION') != -1:
                    version = line.split('=')[1]
                    return '%s' % version.strip()
        except Exception, e:
            self.error(e)



#######################
# User functions
#######################

    def create_client(self, device_ip, device_port0 = 5000, device_port1 = 5001):
        try:
            self._sock0 = self.create_socket(device_ip, device_port0)
            host_ip = self._sock0.getsockname()[0]
            self._sock0.sendall('ETHR %s 1383\x00' % host_ip)
            time.sleep(2)
            self._sock1 = self.create_socket(device_ip, device_port1)
            self._sock1.settimeout(5)
            self.receive()
            return host_ip
        except Exception, e:
            self.rerror(e)



    def get_device_name(self):
        major = self.version_number.split('.')[0]
        if major == '2':
            return 'LeapPad'
        elif major == '1':
            return 'Explorer'
        else:
            return 'Could not determine device'



    def get_version_number(self):
        return self._version_number or self.get_version()

    def set_version_number(self, num):
        self._version_number = num

    version_number = property(get_version_number, set_version_number)



    def get_dftp_version(self):
        try:
            return self._dftp_version or self.find_dftp_version()
        except Exception, e:
            self.rerror(e)

    def set_dftp_version(self, num):
        try:
            self._dftp_version = num
        except Exception, e:
            self.rerror(e)

    dftp_version = property(get_dftp_version, set_dftp_version)




    def download_file(self, local_path, remote_path):
        try:
            if self.exists(remote_path):
                
                if self.sendrtn('RETR %s' % remote_path):
                    f = open(local_path, 'wb')
                    buf = ''
                    self.send('100 ACK: %s\x00' % 0)
                    
                    while True:                    
                        buf = self.receive(8192)
    
                        if buf is False:
                            continue                        
                        elif buf.find('101 EOF') != -1:
                            break
                        else:
                            self.send('100 ACK: %s\x00' % len(buf))
                            f.write(buf)
                    f.close()
        except Exception, e:
            self.rerror(e)
            
            
            
    def upload_file(self, local_path, remote_path):
        try:
            if not os.path.exists(local_path):
                self.error('Path does not exist.')
                
            if self.sendrtn('STOR %s' % remote_path):
                print 'Uploading %s' % os.path.basename(local_path)
                f = open(local_path, 'rb')
                buf = f.read()
                f.close()                
                bytes_sent = self.send(buf)
                ret = True
                
                while ret:
                    ret = self.receive(128)
                    print ret
                    if ret.find('500 Unknown command') != -1:
                        self.error('Problem occured while uploading.')
    
                print 'Sent %s bytes.' % bytes_sent
        
                self.sendrtn('101 EOF')
                return True
            else:
                self.error('Failed to upload file.')
        except Exception, e:
            self.rerror(e)



    def update_firmware(self, lpath):
        try:
            if self._surgeon_dftp_version != self.dftp_version:
                self.error('Device is not in USB boot mode.')

            vn = self.version_number.split('.')[0]
            
            if vn == '1':
                fw_dir = self._lx_fw_dir
                rpath = self._lx_remote_fw_dir
                fw_files = self._lx_fw_files
            
            elif vn == '2':
                fw_dir = self._lpad_fw_dir
                rpath = self._lpad_remote_fw_dir
                fw_files = self._lpad_fw_files
            else:
                self.error('Could not determine device')
                
            if os.path.basename(lpath) != fw_dir:
                
                if os.path.exists(os.path.join(lpath, fw_dir)) and os.path.isdir(os.path.join(lpath, fw_dir)):
                    lpath = os.path.join(lpath, fw_dir)
                else:
                    self.error('Firmware directory not found.')  
                        
            elif not os.path.exists(lpath) or not os.path.isdir(lpath):
                self.error('Firmware directory not found.')

            try:
                self.exists(rpath)
            except:
                self.sendrtn('MKD %s' % rpath)
 
            print 'Updating %s Firmware' % self.get_device_name()
               
            for item in fw_files:
                local_path = os.path.join(lpath, item)
                remote_path = '%s/%s' % (rpath, item)
                    
                if os.path.exists(local_path):

                    try:
                        if self.debug:
                            print '\n-------------------'
                            print 'file: %s' % item 
                            print 'local: %s' % lpath
                            print 'remote: %s'% rpath
                            print '\n'
                        else:
                            self.upload_file(local_path, remote_path)
                            
                    except Exception, e:
                        self.error(e)
                else:
                    print '%s not found, skipped.' % item
                                        
            return True
        except Exception, e:
            self.rerror(e)



    def update_reboot(self):
        try:
            self.sendrtn('RSET')
            self.sendrtn('NOOP')
            self.sendrtn('DCON')
        except Exception, e:
            self.rerror(e)   



#######################
# Filesystem functions
#######################

    def dir_list(self, path):
        try:
            if self.exists(path):
                dir_list = []
                path_arr = self.sendrtn('LIST %s' % path, True)
                
                for path in path_arr:
                    dir_list.append(path[15:].replace('\r', ''))
                    
                return dir_list
            else:
                self.error('Path does not exist.')
        except Exception, e:
            self.rerror(e)



    def is_dir(self, path):
        try:
            if self.exists(path):
                ret_arr = self.sendrtn('LIST %s' % path, True)
                
                if len(ret_arr) > 1:
                    return True
                else:
                    return False
        except Exception, e:
            self.rerror(e)    



    def mkdir(self, path):
        try:
            return self.sendrtn('MKD %s' % path)
        except Exception, e:
            self.rerror(e)


    def rmdir(self, path):
        try:
            if self.exists(path):
                self.sendrtn('RMD %s' % path, False)
        except Exception, e:
            self.rerror(e)


    def rm(self, path):
        try:
            if self.exists(path):
                self.sendrtn('RM %s' % path, False)
        except Exception, e:
            self.rerror(e)

if __name__ == '__main__':
    print 'No demo program available yet.'
