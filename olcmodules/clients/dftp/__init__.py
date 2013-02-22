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
# dftp2.py Version 0.0.3

import os
from olcmodules import config
import olcmodules.firmware.dftp as fwdftp

class client(object):
    def __init__(self, conn_iface, profile, debug=False):
        self.debug = debug
        self._dbg = config.debug(self)
        self._conn_iface = conn_iface
        self._profile = profile
        self._connection = None

        self._name_didj = 'Didj'
        self._name_lx = 'Explorer'
        self._name_lxgs = 'LeapsterGS'
        self._name_lpad = 'LeapPad1'
        self._name_lpad2 = 'LeapPad2'

        self._dftp_version_init = self._profile.get['firmware']['dftp_version']
        
        self._firmware_version = 0
        self._board_id = 0
        self._dftp_version = 0


#######################
# Internal Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'DFTP Error: %s' % e



    def find_dftp_version(self):
        try:
            ret = self.sendrtn('INFO', True)
            
            for line in ret:
                if 'VERSION' in line:
                    version = line.split('=')[1]
                    return '%s' % version.strip()
        except Exception, e:
            self.error(e)



    def get_battery_value(self):
        try:
            # value represents volts x 1000 5.5v = 5500
            # about <4500 and low battery warning comes up
            # 3.8v it shuts down
            ret = self.sendrtn('GETS BATTERYLEVEL', True)
            for value in ret:
                if value.startswith('BATTERYLEVEL'):
                    return value.split('=')[1]
                
            return False
        except Exception, e:
            self.error(e)

#######################
# Internal DFTP Connection Interface Functions
#######################

    def check_dftp_version(self):
        if self._dftp_version_init != self._profile.get['firmware']['dftp_version']:
            self.error('DFTP version mismatch, please change profiles, or reconnect.')

    
    def send(self, data, type='small'):
        self.check_dftp_version()
        return self._connection.send(data, type)

    def receive(self, type='small'):
        self.check_dftp_version()
        return self._connection.receive(type)

    def sendrtn(self, cmd, array=False):
        return self._connection.sendrtn(cmd, array)

    def download_buffer(self, path):
        return self._connection.download_buffer(path)
    
    def upload_buffer(self, buf, rpath):
        return self._connection.upload_buffer(buf, rpath)

    def run_buffer(self, buf):
        return self._connection.run_buffer(buf)
   

#######################
# Client User Information Functions
#######################

    def get_device_name(self):
        bid = self.get_board_id()
        if bid in ['\x00','\x03','\x04','\x05']:
            return self._name_didj
        elif bid <= '\x0A':
            return self._name_lx
        elif bid >= '\x0B' and bid <= '\x0D':
            return self._name_lpad
        elif bid >= '\x200' and bid <= '\x205':
            return self._name_lxgs
        elif bid >= '\x206' and bid <= '\x209':
            return self._name_lpad2
        else:
            return 'Could not determine device'

    device_name = property(get_device_name)



    def get_serial_number(self):
        try:
            ret = self.sendrtn('GETS SERIAL', True)
            for value in ret:
                if value.startswith('SERIAL'):
                    return value.split('=')[1].replace('"','')
                
            return 'Unknown'
        except Exception, e:
            self.rerror(e)
        
    serial_number = property(get_serial_number)



    def get_battery_level(self):
        try:
            ret = float(self.get_battery_value())
            if ret > 0:
                return str(ret/1000)
            elif ret <= 0:
                return 'A/C Power'
            else:
                return 'Unknown'
        except Exception, e:
            self.rerror(e)
    
    battery_level = property(get_battery_level)


    
    def get_board_id(self):
        try:
            if not self._board_id:
                self._board_id = int(self.cat_i('/sys/devices/platform/lf1000-gpio/board_id').strip(), 16)
            return self._board_id
        except Exception, e:
            self.rerror(e)
            
    board_id = property(get_board_id)



    def get_firmware_version(self):
        try:
            if not self._firmware_version:
                path = '/etc/version'
                self._firmware_version = self.cat_i(path).strip()

            return self._firmware_version
        except Exception, e:
            self.rerror(e)

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
            if int(self._profile.get['firmware']['dftp_version']) == 1:
                from olcmodules.clients.dftp import network
                self._connection = network.connection(self._conn_iface)
            elif int(self._profile.get['firmware']['dftp_version']) == 2:
                from olcmodules.clients.dftp import mass_storage
                self._connection = mass_storage.connection(self._conn_iface)
            else:
                self.error('DFTP version could not be determined.')
            
            self._connection.create_client()
        except Exception, e:
            self.rerror(e)



    def disconnect(self):
        try:
            self.send('NOOP\x00')
            self.send('DCON\x00')
            self._connection.disconnect()
        except Exception, e:
            self.rerror(e)



    def reboot(self):
        try:
            self.send('RSET\x00')
            self.disconnect()
        except Exception, e:
            self.rerror(e)



    def reboot_usbmode(self):
        try:
            self.send('UPD8\x00')
            self.disconnect()
        except Exception, e:
            self.rerror(e)



    def update_firmware(self, lpath):
        try:
            if not os.path.exists(lpath):
                self.error('Path does not exist.')

            fw = fwdftp.config(self._profile, lpath)
            paths = fw.get_file_paths()
                
            if not self.exists_i(self._profile.get['firmware']['remote_path']):
                self.mkdir_i(self._profile.get['firmware']['remote_path'])

            print 'Updating %s Firmware' % (self.get_device_name())
               
            for lfpath, rfpath in paths:
                self.upload_file_i(lfpath, rfpath)
                                        
        except Exception, e:
            self.rerror(e)



    def run_script(self, path):
        try:
            if not os.path.exists(path):
                self.error('Script does not exist.')
            elif os.path.isdir(path):
                self.error('Path is not a file.')

            if not self._dbg.run_script(path):
                f = open(path, 'rb')
                buf = f.read()
                f.close()
                self.run_buffer(buf)
        except Exception, e:
            self.rerror(e)


 
    def mount_patient(self, num):
        try:
            if num in ('0', '1', '2'):
                    self._connection.timeout(3)
                    self.sendrtn('SETS MOUNTPATIENT=%s\x00' % num)
                    self._connection.timeout()
            else:
                self.error('Options are 0, 1, and 2')
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
            path_arr = self.send('LIST %s' % path, 'large')
            path_arr = self.receive('large').split('\n')
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
            if not self._dbg.remove(path):
                self.sendrtn('RM %s' % path)
        except Exception, e:
            self.error(e)



    def rmdir_i(self, path):
        try:
            if not self._dbg.remove(path):
                self.sendrtn('RMD %s' % path)
        except Exception, e:
            self.error(e)



    def mkdir_i(self, path):
        try:
            if not self._dbg.make(path):
                self.sendrtn('MKD %s' % path)
        except Exception, e:
            self.error(e)



    def download_file_i(self, lpath, rpath, tab=' '):
        try:
            if not self._dbg.download(lpath, rpath):
                ret_buf = self.download_buffer(rpath)
                
                if ret_buf:
                    f = open(os.path.normpath(lpath), 'wb')
                    f.write(ret_buf)
                    print '%s%s: %s Bytes' % (tab, os.path.basename(rpath), len(ret_buf))
                    f.close()
                else:
                    print '%sError: %s' % (tab, os.path.basename(rpath))
        except Exception, e:
            self.error(e)



    def download_dir_i(self, lpath, rpath, tab=' '):
        try:
            if not os.path.exists(lpath) and not self._dbg.make(lpath):
                os.mkdir(lpath)
                print '%s%s/' % (tab, os.path.basename(lpath))
                tab+=' '
                    
            for item in self.dir_list_i(rpath):
                if item != './' and item != '../':
                    item_lpath = os.path.normpath(os.path.join(lpath, item))
                    item_rpath = os.path.join(rpath, item).replace('\\', '/')
                    rexists = self.exists_i(item_rpath)
                    
                    if rexists and self.is_dir_i(item_rpath):
                        if not os.path.exists(lpath) and not self._dbg.make(item_lpath):
                            os.mkdir(item_lpath)
                            print '%s%s/' % (tab, os.path.basename(item_lpath))
                            
                        self.download_dir_i(item_lpath, item_rpath, tab)

                    elif rexists and not self.is_dir_i(item_rpath):
                        self.download_file_i(item_lpath, item_rpath, tab)
                        
                    else:
                        print '%sSkipped: %s' % (tab, item_rpath)                            
        except Exception, e:
            self.error(e)



    def upload_file_i(self, lpath, rpath, tab=' '):
        try:
            if not self._dbg.upload(lpath, rpath):
                f = open(lpath, 'rb')
                buf = f.read()
                bytes_sent = self.upload_buffer(buf, rpath)
                f.close()                
                
                print '%s%s: %s Bytes.' % (tab, os.path.basename(lpath), bytes_sent)
        except Exception, e:
            self.error(e)



    def upload_dir_i(self, lpath, rpath, tab=' '):
        try:
            if not self.exists_i(rpath) and not self._dbg.make(rpath):
                self.mkdir_i(rpath)
                print '%s%s/' % (tab, os.path.basename(rpath))
                tab+=' '
          
            for item in os.listdir(lpath):
                item_lpath = os.path.join(lpath, item)
                item_rpath = os.path.join(rpath, item).replace('\\', '/')
                lexists = os.path.exists(item_lpath)
                
                if lexists and os.path.isdir(item_lpath):
                    if self.exists_i(item_rpath) and not self._dbg.make(item_rpath):
                        self.mkdir_i(item_rpath)
                        print '%s%s/' % (tab, os.path.basename(item_rpath))

                    self.upload_dir_i(item_lpath, item_rpath, tab)

                elif lexists and not os.path.isdir(item_lpath):
                    self.upload_file_i(item_lpath, item_rpath, tab)

                else:
                    print '%sSkipped: %s' % (tab, item_lpath)                    
        except Exception, e:
            self.error(e)



    def cat_i(self, path):
        try:
            if self.is_dir_i(path):
                self.error('Path is not a file')
            
            ret_buf = self.download_buffer(path)
            if ret_buf:            
                return ret_buf
            else:
                self.error('No data received.')
        except Exception, e:
            self.error(e) 




#######################################################################
# dftp1 connection
#######################################################################








#######################################################################
# dftp2 connection
#######################################################################








if __name__ == '__main__':
    print 'No demo program available yet.'
