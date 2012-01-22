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

import os
import socket
import time

class client(object):
    def __init__(self, net_config, debug=False):
        self.debug = debug
        self._net_config = net_config
        self._sock0 = None
        self._sock1 = None
        
        self._lx_fw_dir = 'Firmware-Base'
        self._lpad_fw_dir = 'firmware'
        
        self._lx_fw_files = ['1048576,8,FIRST.32.rle', '2097152,64,kernel.cbf', '10485760,688,erootfs.ubi']
        self._lpad_fw_files = ['sd/ext4/3/rfs', 'sd/raw/1/FIRST_Lpad.cbf', 'sd/raw/2/kernel.cbf', 'sd/partition/mbr2G.image']

        self._lx_remote_fw_root = '/LF/Bulk/Downloads/'
        self._lx_remote_fw_dir = os.path.join(self._lx_remote_fw_root, self._lx_fw_dir)
        self._lpad_remote_fw_root = '/LF/fuse/'
        self._lpad_remote_fw_dir = os.path.join(self._lpad_remote_fw_root, self._lpad_fw_dir)
        
        self._dftp_version = 0
        self._surgeon_dftp_version = '1.12'
        self._firmware_version = 0
        self._board_id = 0
        
        self._recieve_timeout = .1



#######################
# Internal Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'DFTP Error: %s' % e



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
            if ret:
                retarr = ret.split('\n')
            else:
                self.error('Receiving error.')
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



    def find_dftp_version(self):
        try:
            ret = self.sendrtn('INFO', True)
            
            for line in ret:
                if line.find('VERSION') != -1:
                    version = line.split('=')[1]
                    return '%s' % version.strip()
        except Exception, e:
            self.error(e)



    def get_battery_value(self):
        try:
            ret = self.sendrtn('GETS BATTERYLEVEL', True)
            for value in ret:
                if value.startswith('BATTERYLEVEL'):
                    return value.split('=')[1]
                
            return False
        except Exception, e:
            self.error(e)
            
#######################
# Client User Information Functions
#######################

    def get_device_name(self):
        bid = self.get_board_id()
        if bid > 2:
            return 'LeapPad'
        elif bid == 2:
            return 'Explorer'
        else:
            return 'Could not determine device'

    device_name = property(get_device_name)



    def get_serial_number(self):
        try:
            ret = self.sendrtn('GETS SERIAL', True)
            for value in ret:
                if value.startswith('SERIAL'):
                    return value.split('=')[1].replace('"','')
                
            return 'Unknown.'
        except Exception, e:
            self.rerror(e)
        # parse serial number and return
        
    serial_number = property(get_serial_number)



    def get_battery_level(self):
        try:
            ret = self.get_battery_value()
            if ret:
                ################################################
                # need to figure out values
                return ret
            else:
                return 'Unknown.'
        except Exception, e:
            self.rerror(e)
        # parse battery level
    
    battery_level = property(get_battery_level)


    
    def get_board_id(self):
        try:
            if not self._board_id:
                self._board_id = int(self.cat_i('/sys/devices/platform/lf1000-gpio/board_id').strip())
            return self._board_id
        except Exception, e:
            self.rerror(e)
            
    board_id = property(get_board_id)



    def get_firmware_version(self):
        try:
            if not self._firmware_version:
                path = '/etc/version'
                if self.rfile_check(path):
                    self._firmware_version = self.cat_i(path).strip()
                    
            return self._firmware_version
        except Exception, e:
            self.error(e)

    firmware_version = property(get_firmware_version)



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

#######################
# Client User Command Functions
#######################

    def create_client(self):
        try:
            self._sock0 = self.create_socket(self._net_config.device_id, 5000)
            self._sock0.sendall('ETHR %s 1383\x00' % self._net_config.host_id)
            time.sleep(2)
            self._sock1 = self.create_socket(self._net_config.device_id, 5001)
            self._sock1.settimeout(self._recieve_timeout)
            self.receive()
        except Exception, e:
            self.rerror(e)



    def disconnect(self):
        self._sock0.close()
        self._sock0 = None
        self._sock1.close()
        self._sock1 = None



    def update_firmware(self, lpath):
        try:
            if self._surgeon_dftp_version != self.dftp_version:
                self.error('Device is not in USB boot mode.')
            
            if self.exists_i(self._lpad_remote_fw_root):
                print 'Fuse update.'
                fw_dir = self._lpad_fw_dir
                rpath = self._lpad_remote_fw_dir
                fw_files = self._lpad_fw_files
            
            elif self.exists_i(self._lx_remote_fw_root):
                print 'DFTP update'
                fw_dir = self._lx_fw_dir
                rpath = self._lx_remote_fw_dir
                fw_files = self._lx_fw_files
            
            else:
                self.error('Could not determine update application to use.')
                
            if os.path.basename(lpath) != fw_dir:
                
                if os.path.exists(os.path.join(lpath, fw_dir)) and os.path.isdir(os.path.join(lpath, fw_dir)):
                    lpath = os.path.join(lpath, fw_dir)
                else:
                    self.error('Firmware directory not found.')  
                        
            elif not os.path.exists(lpath) or not os.path.isdir(lpath):
                self.error('Firmware directory not found.')

            if not self.exists_i(rpath):
                self.mkdir_i(rpath)
 
            print 'Updating %s Firmware' % self.get_device_name()
               
            for item in fw_files:
                local_path = os.path.join(lpath, item)
                remote_path = '%s/%s' % (rpath, item)
                    
                if os.path.exists(local_path):

                    try:
                        self.upload_file_i(local_path, remote_path)
                            
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
# Filesystem Interface Functions
#######################

    def exists_i(self, path):
        try:
            ret = self.sendrtn('LIST %s' % path)
    
            if ret.startswith('550'):
                return False
            else:
                return True
        except Exception, e:
            self.error(e)



    def is_dir_i(self, path):
        try:
            path = path.replace('\x00', '')
            ret_arr = self.sendrtn('LIST %s' % path, True)
            if len(ret_arr) > 1 and ret_arr[0].startswith('D'):
                return True
            else:
                return False
        except Exception, e:
            self.error(e)
 


    def dir_list_i(self, path):
        try:
            dir_list = []
            path_arr = self.sendrtn('LIST %s' % path, True)
            
            for path in path_arr:
                path = path[15:].replace('\r', '').replace('\n', '')
                dir_list.append(path)
            
            if len(dir_list) > 0:
                return dir_list
            else:
                return False
        except Exception, e:
            self.error(e)



    def rm_i(self, path):
        try:
            if self.debug:
                print '\n-------------------'
                print 'Remove: %s' % path
                print '\n'
            else:
                self.sendrtn('RM %s' % path)
        except Exception, e:
            self.error(e)



    def rmdir_i(self, path):
        try:
            if self.debug:
                print '\n-------------------'
                print 'Remove: %s' % path
                print '\n'
            else:
                self.sendrtn('RMD %s' % path)
        except Exception, e:
            self.error(e)



    def mkdir_i(self, path):
        try:
            if self.debug:
                print '\n-------------------'
                print 'Made: %s' % path
                print '\n'
            else:
                self.sendrtn('MKD %s' % path)
        except Exception, e:
            self.error(e)



    def lmkdir_i(self, path):
        try:
            if self.debug:
                print '\n-------------------'
                print 'Made: %s' % path
                print '\n'
            else:
                os.mkdir(path)
        except Exception, e:
            self.error(e)



    def download_file_i(self, lpath, rpath):
        try:
            error = False
            if self.debug:
                print '\n-------------------'
                print 'Download'
                print 'Local: %s' % lpath
                print 'Remote: %s' % rpath
                print '\n'                    
            else:
                if self.sendrtn('RETR %s' % rpath):
                    f = open(lpath, 'wb')
                    buf = ''
                    self.send('100 ACK: %s\x00' % 0)
                        
                    while True:                    
                        buf = self.receive(8192)
        
                        if buf is False:
                            continue                        
                        elif buf.find('101 EOF') != -1:
                            break
                        elif buf.lower().find('500 unknown command') != -1:
                            error = True
                            break
                        else:
                            self.send('100 ACK: %s\x00' % len(buf))
                            f.write(buf)
                    if not error:
                        print 'Downloaded %s: %s Bytes' % (os.path.basename(rpath), len(buf))
                    else:
                        print 'Error downloading %s' % os.path.basename(rpath)
                    f.close()
        except Exception, e:
            self.error(e)



    def download_dir_i(self, lpath, rpath):
        try:
            if not os.path.exists(lpath):
                self.lmkdir_i(lpath)
                    
            for item in self.dir_list_i(rpath):
                if item != './' and item != '../':
                    item_lpath = os.path.join(lpath, item)
                    item_rpath = os.path.join(rpath, item).replace('\x00','')
                    
                    if self.is_dir_i(item_rpath) and not os.path.exists(item_lpath):
                        self.lmkdir_i(item_lpath)
                            
                        if self.exists_i(item_rpath):
                            self.download_dir_i(item_lpath, item_rpath)
                        else:
                            print 'Skipped dir: %s' % item_rpath

                    else:
                        if self.exists_i(item_rpath):
                            self.download_file_i(item_lpath, item_rpath)
                        else:
                            print 'Skipped file: %s' % item_rpath
                            
        except Exception, e:
            self.error(e)



    def upload_file_i(self, lpath, rpath):
        try:
            if self.debug:
                print '\n-------------------'
                print 'Local: %s' % lpath
                print 'Remote: %s' % rpath
                print '\n'                    
            else:
                if self.sendrtn('STOR %s' % rpath):
                    f = open(lpath, 'rb')
                    buf = f.read()
                    f.close()                
                    bytes_sent = self.send(buf)
                    ret = True
                        
                    while ret:
                        ret = self.receive()
                            
                        if ret and ret.find('500 Unknown command') != -1:
                            self.error('Problem occured while uploading.')
            
                    print 'Uploaded %s : %s Bytes.' % (os.path.basename(lpath), bytes_sent)                
                    self.sendrtn('101 EOF')
                else:
                    self.error('Failed to upload file.')
        except Exception, e:
            self.error(e)



    def upload_dir_i(self, lpath, rpath):
        try:
            if not self.exists_i(rpath):
                self.mkdir_i(rpath)
          
            for item in os.listdir(lpath):
                item_lpath = os.path.join(lpath, item)
                item_rpath = os.path.join(rpath, item)
                
                if os.path.isdir(item_lpath):
                    self.mkdir_i(item_rpath)
                    
                    if not self.debug:                        
                        self.upload_dir_i(item_lpath, item_rpath)
                else:
                    self.upload_file_i(item_lpath, item_rpath)
                    
        except Exception, e:
            self.error(e)



    def cat_i(self, path):
        try:
            if self.sendrtn('RETR %s' % path):
                buf = ''
                retbuf = ''
                self.send('100 ACK: %s\x00' % 0)
                
                while True:                    
                    buf = self.receive(8192)
        
                    if buf is False:
                        continue                        
                    elif buf.find('101 EOF') != -1:
                        break
                    else:
                        self.send('100 ACK: %s\x00' % len(buf))
                        retbuf += buf
                        
                return retbuf
        except Exception, e:
            self.error(e) 



    def rfile_check(self, path):
        try:
            if self.exists_i(path):
                if not self.is_dir_i(path):
                    return True
                else:
                    self.error('Path is not a file.')
            else:
                self.error('Path does not exist.')
                
        except Exception, e:
            self.rerror(e)



    def rdir_check(self, path):
        try:
            if self.exists_i(path):
                if self.is_dir_i(path):
                    return True
                else:
                    self.error('Path is not a directory.')
            else:
                self.error('Path does not exist.')
                
        except Exception, e:
            self.rerror(e)



    def lfile_check(self, path):
        try:
            if os.path.exists(path):
                if not os.path.isdir(path):
                    return True
                else:
                    self.error('Path is not a file.')
            else:
                    self.error('Path does not exist.')
                
        except Exception, e:
            self.rerror(e)



    def ldir_check(self, path):
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    return True
                else:
                    self.error('Path is not a directory.')
            else:
                    self.error('Path does not exist.')
                
        except Exception, e:
            self.rerror(e)

if __name__ == '__main__':
    print 'No demo program available yet.'
