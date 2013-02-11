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
# dftp4.py Version 0.0.1
import os
import sys
from shlex import split as shlex_split
from subprocess import Popen, PIPE
from olcmodules import config
import olcmodules.firmware.dftp as fwdftp

class client(object):
    def __init__(self, mount_config, debug=False):
        self.debug = debug
        self._dbg = config.debug(self)
        self._mount_config = mount_config
        
        self._name_lpad = 'LeapPad'
        self._name_lx = 'Explorer'
       
        self._surgeon_dftp_version = '1.12'
        
        self._firmware_version = 0
        self._board_id = 0
        self._dftp_version = 0
        self._recieve_timeout = 1

        self._partitions_default = 'leapfrog.cfg'
        self._partitions_config = self._partitions_default
        self._remote_fs_file = '/var/1.2.0.fs'
        
        self._request_large = 10240
        self._request_small = 512

        if sys.platform == 'win32':
            self._sg_raw = 'bin/sg_raw'
        else:
            self._sg_raw = 'sg_raw'

#######################
# Internal Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def rerror(self, e):
        assert False, 'DFTP Error: %s' % e



    def send(self, data, small=True):
        try:
            data_len = len(data)
            bytes_sent = 0
            if small:
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
    
                scsi_cmd = '%s %s -b -s %s -n 2A 80 00 00 00 %s 00 00 %s 00' % (self._sg_raw, self._mount_config.device_id, request_len, lba, trans_len)
                scsi_cmd = shlex_split(scsi_cmd)
                p = Popen(scsi_cmd, stdin=PIPE, stderr=PIPE)
                p.stdin.write(data_p)
                i += request_len
                bytes_sent = bytes_sent + data_p_len

                if not small:
                    ret = self.receive()
                    if not '103 CONT' in ret:
                        print 'NOT 103'
                        break

            if not small:
                self.sendrtn('101 EOF:%s' % str(request_len - data_p_len))

            return bytes_sent
        except Exception, e:
            self.error('Send error: %s' % e)



    def receive(self, small=True):
        try:
            if small:
                request_len = self._request_small
                trans_len = '01'
                lba = '20'
            else:
                request_len = self._request_large
                trans_len = '14'
                lba = '40' 
    
            scsi_cmd = '%s %s -b -r %s -n 28 00 00 00 00 %s 00 00 %s 00' % (self._sg_raw, self._mount_config.device_id, request_len, lba, trans_len)
            scsi_cmd = shlex_split(scsi_cmd)
            p = Popen(scsi_cmd, stdout=PIPE, stderr=PIPE)
            buf = ''

            while 1:
                line = p.stdout.read()
                if line == '':
                    break
                elif '102 BUSY' in line:
                    continue
                else:
                    buf += line
            return buf
        except Exception, e:
            self.error('Receiving error: %s' % e)



    def sendrtn(self, cmd, array=False):
        try:                
            self.send('%s' % cmd)
            ret = ''
            while 1:
                ret_p = self.receive()
                ret += ret_p
                if '200 OK' in ret_p:
                    break
                
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
            self.send('RETR %s' % path.replace('\\', '/'))
            cmd_ret = self.receive().replace('\x00', '')

            if '200 OK' in cmd_ret:
                ret_buf = ''
                buf = ''
                error = False
                    
                while True:                    
                    buf = self.receive(False)
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
            if self.sendrtn('STOR %s' % rpath.replace('\\', '/')):             
                bytes_sent = self.send(buf, False)
                return bytes_sent
            else:
                self.error('Failed to upload file.')
        except Exception, e:
            self.error(e)



    def run_buffer(self, buf):
        try:
            if not buf.startswith('#!/bin/sh'):
                self.error('File does not appear to be valid shell script, missing shebag line.')
            
            if self.sendrtn('RUN'):             
                self.send(buf.replace('\r', ''), False)
                
                while 1:
                    ret = self.sendrtn('GETS SCRIPT_RUNNING', True)
                    if 'SCRIPT_RUNNING=1' in ret[0] :
                        break

                return True
            else:
                self.error('Failed to run script.')
        except Exception, e:
            self.error(e)



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
# Client User Information Functions
#######################

    def get_device_name(self):
        bid = self.get_board_id()
        if bid > 10:
            return self._name_lpad
        elif bid <= 10:
            return self._name_lx
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
                self._board_id = int(self.cat_i('/sys/devices/platform/lf1000-gpio/board_id').strip())
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
            pass
            # nothing to really do hear yet
        except Exception, e:
            self.rerror(e)



    def disconnect(self):
        self.send('DCON')



    def update_firmware(self, lpath):
        try:
            if not os.path.exists(lpath):
                self.error('Path does not exist.')
            elif self._surgeon_dftp_version != self.dftp_version:
                self.error('Device is not in USB boot mode.')
            
            if self.exists_i(fwdftp.FUSE_REMOTE_FW_ROOT):
                utype = 'fuse'
                fw = fwdftp.config(self, utype, self._partitions_config)
                paths = fw.prepare_update(lpath)
            
            elif self.exists_i(fwdftp.DFTP_REMOTE_FW_ROOT):
                utype = 'dftp'
                fw = fwdftp.config(self, utype, self._partitions_config)
                paths = fw.prepare_update(lpath)
                
                if self._partitions_config != self._partitions_default:
                    self.upload_buffer(fw.fs, self._remote_fs_file)     
            else:
                self.error('Could not determine update application to use.')

            print 'Updating %s Firmware with %s' % (self.get_device_name(), utype)
               
            for lfpath, rfpath in paths:
                self.upload_file_i(lfpath, rfpath)
                                        
        except Exception, e:
            self.rerror(e)



    def reboot(self):
        try:
            self.send('RSET')
        except Exception, e:
            self.rerror(e)



    def reboot_usbmode(self):
        try:
            self.send('UPD8')
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
                if self.dftp_version == self._surgeon_dftp_version:
                    self.sendrtn('SETS MOUNTPATIENT=%s' % num)
                else:
                    self.error('Wrong version of DFTP is running.')
            else:
                self.error('Options are 0, 1, and 2')
        except Exception, e:
            self.rerror(e)


    def update_partitions(self, cfg):
        if cfg == '':
            return self._partitions_config
        else:
            if os.path.exists(os.path.join(config.PARTITIONS_PATH, cfg)):
                self._partitions_config = cfg
                return "Set to: %s" % self._partitions_config
            else:
                return 'Config file not found.'
        
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
            path = path.replace('', '')
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

if __name__ == '__main__':
    print 'No demo program available yet.'
