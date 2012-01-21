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
          
        self._lx_remote_fw_dir = os.path.join('/LF/Bulk/Downloads/', self._lx_fw_dir)
        self._lpad_remote_fw_dir = os.path.join('/LF/fuse/', self._lpad_fw_dir)
        
        self._dftp_version = 0
        self._surgeon_dftp_version = '1.12'
        self._firmware_version = 0
        self._board_id = 0



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
# Client User Functions
#######################

    def create_client(self):
        try:
            self._net_config.config_ip()
            self._sock0 = self._net_config.create_socket(self._net_config.device_ip, 5000)
            self._sock0.sendall('ETHR %s 1383\x00' % self._net_config.host_ip)
            time.sleep(2)
            self._sock1 = self._net_config.create_socket(self._net_config.device_ip, 5001)
            self._sock1.settimeout(5)
            self.receive()
        except Exception, e:
            self.rerror(e)


    def disconnect(self):
        self._sock0.close()
        self._sock0 = None
        self._sock1.close()
        self._sock1 = None



    def get_device_name(self):
        bid = self.get_board_id()
        if bid > 2:
            return 'LeapPad'
        elif bid == 2:
            return 'Explorer'
        else:
            return 'Could not determine device'



    def get_board_id(self):
        try:
            if not self._board_id:
                self._board_id = int(self.cat('/sys/devices/platform/lf1000-gpio/board_id').strip())
            return self._board_id
        except Exception, e:
            self.rerror(e)



    def get_firmware_version(self):
        if not self._firmware_version:
            self._firmware_version = self.cat('/etc/version').strip()
        return self._firmware_version

    def set_firmware_version(self, num):
        self._firmware_version = num

    firmware_version = property(get_firmware_version, set_firmware_version)



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



    def update_firmware(self, lpath):
        try:
            if self._surgeon_dftp_version != self.dftp_version:
                self.error('Device is not in USB boot mode.')

            vn = self.firmware_version.split('.')[0]
            
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
                if self.debug:                        
                    print '\n-------------------'
                    print 'make: %s' % rpath
                    print '\n'
                else:
                    self.sendrtn('MKD %s' % rpath)
 
            print 'Updating %s Firmware' % self.get_device_name()
               
            for item in fw_files:
                local_path = os.path.join(lpath, item)
                remote_path = '%s/%s' % (rpath, item)
                    
                if os.path.exists(local_path):

                    try:
                        if self.debug:
                            print '\n-------------------'
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
# Filesystem User Functions
#######################

    def dir_list(self, path):
        try:
            if self.exists(path):
                dir_list = []
                path_arr = self.sendrtn('LIST %s' % path, True)
                
                for path in path_arr:
                    dir_list.append(path[15:].replace('\r', '').replace('\n', ''))
                    
                return dir_list
            else:
                self.error('Path does not exist.')
        except Exception, e:
            self.rerror(e)



    def is_dir(self, path):
        try:
            if self.exists(path):
                path = path.replace('\x00', '')
                ret_arr = self.sendrtn('LIST %s' % path, True)
                print ret_arr
                if len(ret_arr) > 1 and ret_arr[0].startswith('D'):
                    return True
                else:
                    return False
        except Exception, e:
            self.rerror(e)    



    def mkdir(self, rpath):
        try:
            if self.debug:
                print '\n-------------------'
                print 'made: %s' % rpath
                print '\n'
            else:
                self.sendrtn('MKD %s' % rpath)
        except Exception, e:
            self.rerror(e)


    def rmdir(self, rpath):
        try:
            if self.exists(rpath):
                if self.debug:
                    print '\n-------------------'
                    print 'removed: %s' % rpath
                    print '\n'
                else:
                    self.sendrtn('RMD %s' % rpath, False)
        except Exception, e:
            self.rerror(e)


    def rm(self, rpath):
        try:
            if self.exists(rpath):
                if self.debug:
                    print '\n-------------------'
                    print 'removed: %s' % rpath
                    print '\n'
                else:
                    self.sendrtn('RM %s' % rpath, False)
        except Exception, e:
            self.rerror(e)



    def download_file(self, lpath, rpath):
        try:
            if not self.exists(rpath):
                self.error('Path does not exist.')
                
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote: %s' % rpath
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
                        else:
                            self.send('100 ACK: %s\x00' % len(buf))
                            f.write(buf)
                    print 'Downloaded %s : %s Bytes' % (os.path.basename(rpath), len(buf))
                    f.close()
        except Exception, e:
            self.rerror(e)



    def download_dir(self, lpath, rpath):
        try:
            if not os.path.exists(lpath):
                if self.debug:                        
                    print '\n-------------------'
                    print 'make: %s' % rpath
                    print '\n'
                else:
                    os.mkdir(lpath)
              
            for item in self.dir_list(rpath):
                if item != './' and item != '../':
                    item_lpath = os.path.join(lpath, item)
                    item_rpath = os.path.join(rpath, item).replace('\x00','')
                    
                    if self.is_dir(item_rpath):
                        if self.debug:                        
                            print '\n-------------------'
                            print 'make: %s' % item_lpath
                            print '\n'
                        else:
                            os.mkdir(item_lpath)
                        self.download_dir(item_lpath, item_rpath)
                    else:
                        if self.debug:
                            print '\n-------------------'
                            print 'local: %s' % item_lpath
                            print 'remote: %s' % item_rpath
                            print '\n'
                        else: 
                            try:
                                if self.exists(item_rpath):
                                    self.download_file(item_lpath, item_rpath)
                            except:
                                print 'not downloaded %s' % item_rpath
        except Exception, e:
            self.error(e)



    def upload_file(self, lpath, rpath):
        try:
            if not os.path.exists(lpath):
                self.error('Path does not exist.')
                
            if self.debug:
                print '\n-------------------'
                print 'local: %s' % lpath
                print 'remote: %s' % rpath
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
                    return True
                else:
                    self.error('Failed to upload file.')
        except Exception, e:
            self.rerror(e)



    def upload_dir(self, lpath, rpath):
        try:
            if os.path.isdir(lpath):
                try:
                    self.exists(rpath)
                except:
                    if self.debug:                        
                        print '\n-------------------'
                        print 'make: %s' % rpath
                        print '\n'
                    else:
                        self.mkdir(rpath)
                  
                for item in os.listdir(lpath):
                    item_lpath = os.path.join(lpath, item)
                    item_rpath = os.path.join(rpath, item)
                    
                    if os.path.isdir(item_lpath):
                        if self.debug:                        
                            print '\n-------------------'
                            print 'make: %s' % item_rpath
                            print '\n'
                        else:
                            self.mkdir(item_rpath)
                            self.upload_dir(item_lpath, item_rpath)
                    else:
                        if self.debug:
                            print '\n-------------------'
                            print 'local: %s' % item_lpath
                            print 'remote: %s' % item_rpath
                            print '\n'
                        else: 
                            self.upload_file(item_lpath, item_rpath)                    
        except Exception, e:
            self.error(e)
            
            
            
    def cat(self, rpath):
        try:
            if self.exists(rpath):
                
                if self.sendrtn('RETR %s' % rpath):
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
            self.rerror(e)

if __name__ == '__main__':
    print 'No demo program available yet.'
