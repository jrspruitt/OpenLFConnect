#!/usr/bin/env python
##############################################################################
#    OpenLFConnect verson 0.1
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

# OpenLFConnect version 0.1.0

import os
import cmd
import sys

from services.networking import config
from services.pager import pager
from services.dftp import client as dftpclient
from services.local import filesystem
from services.didj import client as didjclient
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# opendidj connect
# set app disconnected after reboot
# test more windows paths \/
# remove host_ip from dftp connect
# download/extract firmwares
# attempt Lpad integration
# clean out unused/unnecessary code
# final tests
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

class OpenLFConnect(cmd.Cmd, object):
    def __init__(self):
        cmd.Cmd.__init__(self)

        self._host_ip_default = '169.254.0.1'

        self._prompt_suffix = '> '
        self.prompt = 'local%s' % self._prompt_suffix

        self._networking = config()
        self._dftp = dftpclient()
        self._didj = didjclient()
        self._pager = pager()
        self._local_fs = filesystem()
        
        self._is_connected = False
        self._is_mounted = False

        self._remote_path_module = None
        self._local_path_module = self._local_fs
        self._path_module = self._local_path_module
        
        self._local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files')).replace('\\', '/')

        self._remote_path= '/'
        self._path = ''
        self._remote_set = True
        
        self._remote_path_dir_list = []
        self._local_path_dir_list = []
        self._path_dir_list = []

        self.set_local()


#######################
# OpenLFConnect.py
#######################
    def error(self, e):
        assert False, '%s' % e

    def perror(self, e):
        print '%s' % e

    def get_is_connected(self):
        if self._is_connected:
            return self._is_connected 
        else:
            self.error('Device not connected')
    
    def set_is_connected(self, status):
        self._is_connected = status

    is_connected = property(get_is_connected, set_is_connected)



    def get_is_mounted(self):
        if self._is_mounted:
            return self._is_mounted 
        else:
            self.error('Device not mounted')
    
    def set_is_mounted(self, status):
        self._is_mounted = status

    is_mounted = property(get_is_mounted, set_is_mounted)



    def get_path_prefix(self):
        if sys.platform == 'win32' and not self._remote_set:
            return '%s/' % os.path.splitdrive(self._local_path)[0]
        elif sys.platform == 'linux2':
            return '/'
        else:
            return '/'

            
    def path_format(self, stub):
        chomp = False
        spath = self._path
            
        stub = stub.replace('//', '/')
        if stub == '/':
            stub = ''
            spath = self.get_path_prefix()
        else:
            if spath.endswith('/') and spath != self.get_path_prefix():
                spath = spath[0:-1]

            if stub.startswith('/'):
                stub = stub[1:]
                spath = self.get_path_prefix()

            if not spath.startswith(self.get_path_prefix()):
                spath = '%s%s' % (self.get_path_prefix(), spath)
                
            if stub.startswith(('../', '..', './')):
                chomp = True
                while chomp:
                    if stub.startswith('../'):
                        stub = stub[3:]
                        spath = os.path.dirname(spath)
                    elif stub.startswith('..'):
                        stub = stub[2:]
                        spath = os.path.dirname(spath)
                    elif stub.startswith('./'):
                        stub = stub[2:]
                    else:
                        chomp = False
        abspath = os.path.join(spath, stub)
        if sys.platform == 'win32' and self._is_connected:
            abspath = abspath.replace('\\','/')
        return (spath, stub, abspath)



    def path_completion(self, text, line, begidx, endidx):
        try:
            mline = line.partition(' ')[2]
            paths = self.path_format(mline)
            spath = paths[0]
            stub = paths[1]
            list_arr = [s for s in self.get_dir_list(spath) if s.startswith(stub) and not s == stub]

            if len(list_arr) == 0:
                parent_dir = os.path.dirname(stub)
                if parent_dir.startswith('/'):
                    parent_dir = parent_dir[1:]
                list_arr = [item for item in self.get_dir_list(os.path.join(spath, parent_dir)) if item.startswith(os.path.basename(stub))]
    
            return list_arr
        except:
            pass



    def get_dir_list(self, path):
        try:
            dlist = self._path_module.dir_list(path)
            dir_list = []
            for item in dlist:
                if not item.startswith(('../', './')):
                    dir_list.append(item)
            dir_list.sort(key=str.lower)
            return dir_list
        except Exception, e:
            self.error(e)



    def set_path(self, path):
        if self._remote_set:
            if self._path_module.is_dir(path):
                self.set_remote_path(path)
            else:
                self.error('Is not a directory')
        else:
            if self._local_path_module.is_dir(path):
                self.set_local_path(path)
            else:
                self.error('Is not a directory')



    def set_remote(self):
        if self.is_connected:
            self._path_dir_list = self._remote_path_dir_list
            self._path_module = self._remote_path_module
            self._path = self._remote_path
            self._remote_set = True
            self.prompt = 'remote%s' % self._prompt_suffix



    def set_local(self):
        self._path_dir_list = self._local_path_dir_list
        self._path_module = self._local_path_module
        self._path = self._local_path
        self._remote_set = False
        self.prompt = 'local%s' % self._prompt_suffix



    def set_remote_path(self, path):
        lists = self.get_dir_list(path)
        self._remote_path_dir_list = lists
        self._remote_path = path
        self.set_remote()
        

    def set_local_path(self, path):
        lists = self.get_dir_list(path)
        self._local_path_dir_list = lists
        self._local_path = path
        self.set_local()
        

    def connection_path_init(self, module):
        self.set_local_path(self._local_path)
        self._remote_path_module = module
        self.set_remote_path(self._remote_path)

        
#######################
# didj.py
#######################     
    def complete_didj_mount_point(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)



    def do_didj_mount_point(self, s):
        """
didj_mount_point path|drive letter\n Manually configure the local Didj directory.
        """
        try:
            
            try:
                if self.is_mounted:
                    self.error('Device is already mounted')
            except: pass

            if s != '':
                path = self.path_format(s)[2]
            else:
                path = s
            
            self._didj.mount_point = path
        except Exception, e:
            self.perror(e)



    def do_didj_mount(self, s):
        """
didj_mount [mount name] \n Unlock Didj to allow it to mount on host system. 
Mount name would be the directory created in /media, or on windows the drive label, defaults to 'didj'. Case insensative.
        """
        try:
            if s != '':
                mount_name = s
            else:
                mount_name = self._didj.mount_name

            dev_id = self._local_fs.get_device_id()
            self._didj.mount(dev_id)
            self._didj.mount_path = self._local_fs.get_mount_path(mount_name)
            print 'Mounted on: %s' % self._didj.mount_path
            self.is_mounted = True
        except Exception, e:
            self.perror(e)



    def do_didj_umount(self, s):
        """
didj_umount\n Lock Didj which will unmount on host system. In Linux may have to use OS's umount command.
        """
        try:
            #if self.is_mounted:
            self._didj.umount()
            self.is_mounted = False
        except Exception, e:
            self.perror(e)



    def do_didj_eject(self, s):
        """
didj_eject\n Eject Didj which will unmount on host system, and trigger a firmware update if available. In Linux may have to use OS's eject command.
        """
        try:
            #if self.is_mounted:
            self._didj.eject()
            self.is_mounted = False
        except Exception, e:
            self.perror(e)



    def complete_didj_update(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)



    def do_didj_update(self, s):
        """
didj_update\n Update Didj firmware and bootloader
        """
        try:
            if self.is_mounted:
                if s != '':
                    path = self.path_format(s)[2]
                else:
                    path = self._local_path
                self._didj.mount_path
                fw_paths = self._didj.get_firmware_paths(path)
                self._local_fs.cpdir(fw_paths[0], fw_paths[1])
                bl_paths = self._didj.get_bootloader_paths(path)
                self._local_fs.cpdir(bl_paths[0], bl_paths[1])
                self._didj.eject()
                self.is_mounted = False
        except Exception, e:
            self.perror(e)



    def complete_didj_update_firmware(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)



    def do_didj_update_firmware(self, s):
        """
didj_update_firmware\n Update Didj firmware and bootloader
        """
        try:
            if self.is_mounted:
                if s != '':
                    path = self.path_format(s)[2]
                else:
                    path = self._local_path
                self._didj.mount_path
                fw_paths = self._didj.get_firmware_paths(path)
                self._local_fs.cpdir(fw_paths[0], fw_paths[1])
                self._didj.eject()
                self.is_mounted = False
        except Exception, e:
            self.perror(e)




    def complete_didj_update_bootloader(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)



    def do_didj_update_bootloader(self, s):
        """
didj_update\n Update Didj firmware and bootloader
        """
        try:
            if self.is_mounted:
                if s != '':
                    path = self.path_format(s)[2]
                else:
                    path = self._local_path
                self._didj.mount_path
                bl_paths = self._didj.get_bootloader_paths(path)
                self._local_fs.cpdir(bl_paths[0], bl_paths[1])
                self._didj.eject()
                self.is_mounted = False
        except Exception, e:
            self.perror(e)


    def do_didj_update_cleanup(self, s):
        """
didj_update_cleaup\n Remove Didj firmware and bootloader from device.
        """
        try:
            if self.is_mounted:
                self._didj.cleanup()
        except Exception, e:
            self.perror(e)

#######################
# networking.py
#######################

    def connect(self, host_ip):
        """
connect [host ip]\n creats a listener to get the device's IP, if found, attempts to set up dftp client.
        """
        #todo test its an IP
        if host_ip != '':
            self._host_ip_default = host_ip
        
        try:
            self._networking.host_ip = self._host_ip_default
            self._networking.retrieve_ip()
            print 'Device IP: %s' % self._networking.device_ip
        except Exception, e:
            self.error(e)



    def do_ip(self, s):
        """
ip [host|device]\n Returns the assigned IP address or both if neither is choosen.
        """
        hip = self._networking.host_ip
        dip = self._networking.device_ip
        
        if not hip:
            hip = 'Not Set'
        if not dip:
            dip = 'Not Set'

        if s == 'host':
            print '%s' % hip
        elif s == 'device':
            print '%s' % dip
        else:
            print 'Host:\t\t%s\nDevice:\t\t%s' % (hip, dip)



    def do_set_device_ip(self, s):
        """
set_device_ip <IP>\n Sets the devices IP to a known value, this will not reconfigure the devices's IP, should be set to it's actual IP.
        """
        self.is_connected
        self._networking.device_ip(s)
        print 'Device IP set to %s' % s



#######################
# pager.py
#######################    

    def complete_boot_surgeon(self, text, line, begidx, endidx):
        try:
            remote = self._remote_set
            if remote:
                self.set_local()
            comp = self.path_completion(text, line, begidx, endidx)
            if remote:
                self.set_remote()
            return comp
        except Exception, e:
            self.perror(e)



    def do_boot_surgeon(self, s):
        """
boot_surgeon <file_name>\n Uploads a Surgeon.cbf file to a device in USB Boot mode.
        """
        try:
            if s != '':
                path = self.path_format(s)[2]
            else:
                path = s
                
            if not self._local_fs.is_dir(path):
                dev_id = self._local_fs.get_device_id()
                self._pager.upload_firmware(path, dev_id)
            else:
                self.error('Path is not a file.')
        except Exception, e:
            self.perror(e)



#######################
# dftp.py
#######################

    def send(self, cmd):
        try:
            print self._dftp.sendrtn(cmd)
        except Exception, e:
            self.error(e)
            
                    

    def do_dftp_connect(self, s):
        """
dftp_connect_\n Connect to device for dftp session.
        """
        try:
            self.connect(s)
            self._networking.host_ip = self._dftp.create_client(self._networking.device_ip, self._networking.host_ip)
            self.is_connected = True
            self.connection_path_init(self._dftp)
            self.set_remote()
        except Exception, e:
            self.perror(e)



    def complete_dftp_update(self, text, line, begidx, endidx):
        try:
            remote = self._remote_set
            if remote:
                self.set_local()
            comp = self.path_completion(text, line, begidx, endidx)
            if remote:
                self.set_remote()
            return comp
        except Exception, e:
            self.perror(e)



    def do_dftp_update(self, s):
        """
update <Firmware Path>\n Uploads and flashes to NAND the files in <Firmware Path>. Files must conform to LF naming conventions.
        """
        try:
            self.is_connected
            remote = self._remote_set
            if remote:
                self.set_local()
            if s != '':
                path = self.path_format(s)[2]
            else:
                path = s
            if not self._path_module.is_dir(path):
                self._dftp.update_firmware(path)
        except Exception, e:
            self.perror(e)


    
    def do_dftp_reboot(self, s):
        """
update_reboot\n After running update, run this to trigger a reboot
        """
        try:
            self.is_connected
            self._dftp.update_reboot()
            self.set_is_connected = False
        except Exception, e:
            self.perror(e)



    def do_send(self, s):
        """
send <raw command>\n Advanced use only, don't know, probably shouldn't.
        """
        try:
            self.is_connected
            self.send(s)
        except Exception, e:
            self.perror(e)



#######################
# Module independant
# Filesystem commands
#######################

    def do_remote(self, s):
        """
remote\n Set to remote device for filesystem navigation.
        """
        try:
            self.is_connected
            self.set_remote()
        except Exception, e:
            self.perror(e)


        
    def do_local(self, s):
        """
remote\n Set to local host for filesystem navigation.
        """
        try:
            #self.is_connected
            self.set_local()
        except Exception, e:
            self.perror(e)



    def do_cwdr(self, s):
        """
cwdr\n Print current remote directory path.
        """
        print self._remote_path



    def do_cwdl(self, s):
        """
cwdl\n Print current local directory path.
        """
        print self._local_path



    def do_exit(self, s):
        """
exit\n Exit OpenLFConnect
        """
        sys.exit()



    def complete_ls(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)



    def do_ls(self, s):
        """
ls [path]\n List remote directory contents.
        """            
        try:
            abspath = self.path_format(s)[2]
            if abspath == '':
                abspath = self.get_path_prefix()
            if self._path_module.is_dir(abspath):
                dlist = self.get_dir_list(abspath)
                flist = []
                for item in dlist:
                    if item[-1:] == '/':
                        print '%s' % item
                    else:
                        flist.append(item)
                flist.sort(key=str.lower)
                for item in flist:
                    print '%s' % item
            else:
                self.perror('Is not a directory.')

        except Exception, e:
            self.perror(e)



    def complete_cd(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)




    def do_cd(self, s):
        """
cd <path>\n Change directories.
        """
        try:
            self.set_path(self.path_format(s)[2])
        except Exception, e:
            self.perror(e)



    def complete_mkdir(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)



    def do_mkdir(self, s):
        """
mkdir <directory name>\n Create directory.
        """
        try:
            abspath = self.path_format(s)[2]
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                if self._path_module.is_dir(os.path.dirname(abspath)):
                    self._path_module.mkdir(abspath)
                else:
                    print 'Path is not in a directory'
        except Exception, e:
            self.perror(e)



    def complete_rmdir(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)


    
    def do_rmdir(self, s):
        """
rmd <directory path>\n Delete directory.
        """
        try:
            abspath = self.path_format(s)[2]
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                if self._path_module.is_dir(os.path.dirname(abspath)):
                    self._path_module.rmdir(abspath)
                else:
                    print 'Path is not in a directory'
        except Exception, e:
            self.perror(e)



    def complete_rm(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except Exception, e:
            self.perror(e)



    def do_rm(self, s):
        """
rm <file name>\n Delete file.
        """
        try:
            abspath = self.path_format(s)[2]
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                if not self._path_module.is_dir(abspath):
                    self._path_module.rm(abspath)
                else:
                    print 'Path is not in file'
        except Exception, e:
            self.perror(e)



#######################
# Module independant
# Upload/Download commands
#######################

    def complete_upload(self, text, line, begidx, endidx):
        try:
            self.is_connected
            remote = self._remote_set
            if remote:
                self.set_local()
            comp = self.path_completion(text, line, begidx, endidx)
            if remote:
                self.set_remote()
            return comp
        except Exception, e:
            self.perror(e)



    def do_upload(self, s):
        """
upload <local filename>\n Upload file to device, Will overwrite with out prompt.
        """
        try:
            self.is_connected
            remote = self._remote_set
            
            if remote:
                self.set_local()
            abspath = self.path_format(s)[2]
            if not self._path_module.is_dir(abspath):
                self.set_remote()
                
                remote_path = os.path.join(self._path, os.path.basename(abspath))
                if sys.platform == 'win32':
                    remote_path = remote_path.replace('\\', '/')
                    
                self._path_module.upload_file(abspath, remote_path)
                if not remote:
                    self.set_local()
            else:
                self.error('Path not set to a file.')
        except Exception, e:
            self.perror(e)



    def complete_download(self, text, line, begidx, endidx):
        try:
            self.is_connected
            remote = self._remote_set
            if not remote:
                self.set_remote()
            comp = self.path_completion(text, line, begidx, endidx)
            if not remote:
                self.set_local()
            return comp
        except Exception, e:
            self.perror(e)



    def do_download(self, s):
        """
download <remote filename>\n Download file from device, Will overwrite with out prompt.
        """
        try:
            self.is_connected
            remote = self._remote_set
            if not remote:
                self.set_remote()
            abspath = self.path_format(s)[2]
            if not self._path_module.is_dir(abspath):
                self._path_module.download_file(os.path.join(self._local_path, os.path.basename(abspath)), abspath)
                if not remote:
                    self.set_local()
            else:
                self.error('Path not set to a file.')

        except Exception, e:
            self.perror(e)



    def do_enable_sshd(self, s):
        """
enable_sshd\n Uploads two custom files, to enable the ssh server on boot, files found in <app path>/files/LX/sshd_enable/
        """
        try:
            self.is_connected
            remote = self._remote_set
            if not remote:
                self.set_remote()
            self._path_module.upload_file('files/LX/enable_sshd/rcS', '/etc/init.d/rcS')
            self._path_module.upload_file('files/LX/enable_sshd/sshd_config', '/etc/ssh/sshd_config')
            if not remote:
                self.set_local()
        except Exception, e:
            self.perror(e)



if __name__ == '__main__':

    OpenLFConnect().cmdloop()
        
