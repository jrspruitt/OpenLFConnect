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
import cmd
import sys

from olcmodules.system.networking import connection as net_connection
from olcmodules.system.mount import connection as mount_connection
from olcmodules.system.interface import config as conn_iface

from olcmodules.clients.pager import client as pager_client
from olcmodules.clients.dftp import client as dftp_client
from olcmodules.clients.local import client as local_client
from olcmodules.clients.didj import client as didj_client
from olcmodules.clients.interface import filesystem as fs_iface

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# TODO
# documentation
# download/extract firmwares?
# LX add addres/size to bare named files
# Didj needs_repair fix (bootflags.jffs2)?
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

class OpenLFConnect(cmd.Cmd, object):
    def __init__(self):
        cmd.Cmd.__init__(self)
        print 'OpenLFConnect Version 0.3'
        self.debug = False
        
        self._prompt_suffix = '> '
        self.prompt = 'local%s' % self._prompt_suffix

        self._dftp_client = None
        self._didj_client = None
        self._pager_client = None
        self._local_client = local_client(self.debug)
        self._remote_client = None
        self._remote_conn = None
        
        self._remote_set = False
        
        self._local_fs = fs_iface(self._local_client)
        self._remote_fs = None        
        self._fs = self._local_fs
        
        self._local_path_init = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files')).replace('\\', '/')
        self._local_path = self._local_path_init
        self._remote_path_init = '/'
        self._remote_path = self._remote_path_init        
        self._path = ''        

        self._host_id = ''
        self._device_id = ''
        
        self.set_local(self._local_path)



#######################
# OpenLFConnect.py
# Internal Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def perror(self, e):
        print '%s' % e

#######################
# Remote Local Functions
#######################

    def set_remote(self, path=''):
        if path:
            self._remote_path = path
        self._fs = self._remote_fs
        self._path = self._remote_path
        self._remote_set = True
        self.prompt = 'remote%s' % self._prompt_suffix



    def set_local(self, path=''):
        if path:
            self._local_path = path
        self._fs = self._local_fs
        self._path = self._local_path
        self._remote_set = False
        self.prompt = 'local%s' % self._prompt_suffix



    def is_remote(self, rmod=False, ret_bool=False):
        error = ''
        connected = False
        
        if rmod is None:
            rmod = True

        if not self._remote_conn:
            error = 'No connection established.'            
        else:
            connected = self._remote_conn.is_connected()

            if not connected:
                self.remote_destroy()
                self.error('Device not connected')
    
            elif connected and rmod is False:
                return True
                
            elif connected and rmod is not self._remote_client:
                self.error('Device connected, but wrong client is running.')
                
            elif connected and rmod is self._remote_client:
                return True
                
            else:
                self.remote_destroy()
                self.error('Something is wrong with your connection.')

        if ret_bool:
            return False
        else:
            self.error(error)
        


    def remote_connection_init(self, conn_iface, fs_iface, client):
        self._remote_client = client
        self._remote_conn = conn_iface
        self._remote_fs = fs_iface



    def remote_path_init(self):
        if self._remote_conn:
            self.set_remote(self._remote_conn.root_dir)
        else:
            self.set_local()
            self.error('No remote module present.')
 
 
 
    def remote_destroy(self):
        self._remote_client = None
        self._remote_conn = None
        self._remote_fs = None
        self._remote_set = False
        self._remote_path = self._remote_path_init
        self.set_local(self._local_path_init)

#######################
# Path Formatting Functions
#######################

    def set_path(self, path):
        if self._remote_set:            
            if self._fs.is_dir(path):
                self.set_remote('%s' % path)
            else:
                self.error('Is not a directory')
        else:
            
            if self._local_fs.is_dir(path):
                self.set_local('%s' % path)
            else:
                self.error('Is not a directory')



    def get_path_prefix(self):
        if sys.platform == 'win32' and not self._remote_set:
            return '%s/' % os.path.splitdrive(self._local_path)[0]
        elif sys.platform == 'linux2':
            return '/'
        else:
            return '/'



    def get_abspath(self, stub):
        if stub.startswith(self.get_path_prefix()):
            path = stub
        else:
            path = os.path.join(self._path, stub)
        if sys.platform == 'win32' and self._remote_set:
            ret = os.path.normpath(path).replace('\\', '/')
        else:
            ret = os.path.normpath(path)

        return ret

#######################
# Path Completion Functions
#######################

    def is_empty(self, s):
        if s == '':
            self.error('No path was set.')
        else:
            return True



    def get_dir_list(self, path):
        try:
            dlist = self._fs.dir_list(path)
            dir_list = []
            
            for item in dlist:
                if not item.startswith(('../', './')):
                    dir_list.append(item)
                    
            dir_list.sort(key=str.lower)
            return dir_list
        except Exception, e:
            self.error(e)



    def path_completion(self, text, line, begidx, endidx):
        try:
            mline = line.partition(' ')[2]
            if mline[-1:] != '/' and not mline == '':
                abspath = os.path.dirname(self.get_abspath(mline))
                stub = '%s' % os.path.basename(mline)
            else:
                abspath = '%s/' % self.get_abspath(mline)
                stub = ''
                
            return [s for s in self.get_dir_list(abspath) if s.startswith(stub)]
        except:
            return ''



    def complete_local(self, text, line, begidx, endidx):
        try:
            remote = self._remote_set
            
            if remote:
                self.set_local()
            comp = self.path_completion(text, line, begidx, endidx)
            
            if remote:
                self.set_remote()
            return comp        
        except:
            pass



    def complete_remote(self, text, line, begidx, endidx):
        try:
            self.is_remote()
            remote = self._remote_set
            
            if not remote:
                self.set_remote()
                
            comp = self.path_completion(text, line, begidx, endidx)
            
            if not remote:
                self.set_local()
                
            return comp
        except:
            pass



    def complete_path(self, text, line, begidx, endidx):
        try:
            return self.path_completion(text, line, begidx, endidx)
        except:
            pass



#######################
# User Functions
#######################
# need to fix this, should be able to set reference only instead of specifically
    def do_debug_on(self, s):
        """
Usage:
    debug_on

Setting this prevents updates from actually happening, instead printing the files that would have been uploaded.
        """
        self.debug = True
        if self._dftp_client:
            self._dftp_client.debug = self.debug
        if self._didj_client:
            self._didj_client.debug = self.debug
        if self._remote_conn:
            self._remote_conn.debug = self.debug
        if self._local_client:
            self._local_client.debug = self.debug
        if self._pager_client:
            self._pager_client.debug = self.debug

 
    def do_debug_off(self, s):
        """
Usage:
    debug_off

Turns off debugging mode. Updates will be attempted.
        """
        self.debug = False
        if self._local_fs:
            self._local_fs.debug = self.debug
        if self._remote_fs:
            self._remote_fs.debug = self.debug



    def do_is_connected(self, s):
        print self._didj_client
        if self._remote_conn is not None and self._remote_conn.is_connected():
            print 'Device is connected' 
        else:
            self.perror('Device not connected')

#######################
# Internal Connection Config Functions
# Connection Config Functions
#######################

    def get_device_id(self):
        return self._device_id

    def set_device_id(self, did):
        self._device_id = did

    device_id = property(get_device_id, set_device_id)



    def get_host_id(self):
        return self._host_id

    def set_host_id(self, hid):
        self._host_id = hid

    host_id = property(get_host_id, set_host_id)
                         
#######################
# User Connection Config Functions
# system.mount.connection
#######################

    def do_get_device_id(self, s):
        """
Usage:
    get_dev_id

Returns the currently configured device id.
        """
        return self.device_id

    def do_set_device_id(self, s):
        """
Usage:
    set_dev_id <device id>

Manually configures the device id, in Linux its the generic scsi
device file, ex. /dev/sg2 or harddrive /dev/sdb , in windows its the PhysicalDrive ex. PD1.
This needs to be set before attempting to connect or set up a network connection.
This is only needed if for some reason, OpenLFConnect can not determine it.
        """
        self.device_id = s



    def do_get_mount_point(self, s):
        """
Usage:
    get_mount_point

Returns the currently configured mount point.
        """
        return self.host_id

    def do_set_mount_point(self, s):
        """
Usage:
    set_mount_point <mount point>

Manually configure the mount point, ex. Linux /media/didj, ex. Windows D:\
This needs to be set before a attempting to connect to or mount the device.
This is only needed if for some reason, OpenLFConnect can not determine it.
        """
        self.host_id = s

#######################
# Connection Config User Functions
# system.networking.connection
#######################

    def get_device_ip(self):
        """
Usage:
    get_device_ip

Returns currently configured device IP.
        """
        return self.device_id

    def do_set_device_ip(self, s):
        """
Usage:
    set_device_ip <IP>

Manually set the device's IP to a known value, this will not reconfigure the devices's IP, should be set to it's actual IP.
This should be set before connecting to a device, or establishing a network connection.
        """
        self.device_id = s



    def do_get_host_ip(self):
        """
Usage:
    get_host_ip

Returns currently configured host IP.
        """
        return self.host_id

    def do_set_host_ip(self, s):
        """
Usage:
    set_host_ip <IP>

Manually set the host's IP to a known value, this will not reconfigure the host's IP, should be set to it's actual IP.
This should be set before connecting to a device, or establishing a network connection.
        """
        self.host_id = s

#######################
# Didj Internal Functions
# clients.didj
#######################

    def complete_didj_update_bootloader(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)



    def complete_didj_update(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)



    def complete_didj_update_firmware(self, text, line, begidx, endidx):
        return self.path_complete_local(text, line, begidx, endidx)



#######################
# Didj User Functions
# clients.didj
#######################

    def do_didj_mount(self, s):
        """
Usage:
    didj_mount [mount name]

Unlock Didj to allow it to mount on host system.
        """
        try:
            if not self.is_remote(None, True):
                mc = conn_iface(mount_connection(self.device_id, self.host_id, self.debug))
                self._didj_client = didj_client(mc, self.debug)                
                self.remote_connection_init(mc, fs_iface(local_client(self.debug)), self._didj_client)
                self._didj_client.mount()
                self.remote_path_init()
                print 'Mounted on: %s' % self._remote_conn.host_id
            else:
                self.error('Didj already running.')
        except Exception, e:
            self.perror(e)



    def do_didj_umount(self, s):
        """
Usage:
    didj_umount

Lock Didj which will un mount on host system. Only seems to work in Windows.
        """
        try:
            self.is_remote(self._didj_client)
            self._didj_client.umount()
            self.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_didj_eject(self, s):
        """
Usage:
    didj_eject

Eject the Didj which will unmount on host system, if the firmware updates are 
on the Didj, an update will be triggered. If they are not, it will ask you to unplug it. For
Linux hosts, you'll also have to eject it from the system.
        """
        try:
            self.is_remote(self._didj_client)
            self._didj_client.eject()
            self.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_didj_update(self, s):
        """
Usage:
    didj_update <path>

CAUTION:
!!Attempts to flash firmware, could potentially be harmful.!!
!!Make sure Battery's are Fresh, or A/C adpater is used!!

Update Didj firmware and bootloader. Files must be in bootloader-LF_LF1000 and firmware-LF_LF1000 directories.
Searches from the current local directory for the top level directory of the firmware, local path can be directly inside the top level directory or one above it.
 MD5 files will be created automatically.
        """
        try:
            self.is_remote(self._didj_client)
            abspath = self.get_abspath(s)
            self._didj_client.upload_firmware(abspath)
            self._didj_client.upload_bootloader(abspath)
            if not self.debug:      
                self._didj_client.eject()
                self.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_didj_update_firmware(self, s):
        """
Usage:
    didj_update_firmware <path>

CAUTION:
!!Attempts to flash firmware, could potentially be harmful.!!
!!Make sure Battery's are Fresh, or A/C adpater is used!!

Update Didj firmware. Files must be in firmware-LF_LF1000 directory.
Searches from the current local directory for the top level directory of the firmware, local path can be directly inside the top level directory or one above it.
MD5 files will be created automatically.
        """
        try:
            self.is_remote(self._didj_client)
            abspath = self.get_abspath(s)
            self._didj_client.upload_firmware(abspath)
            if not self.debug:                
                self._didj_client.eject()
                self.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_didj_update_bootloader(self, s):
        """
Usage:
    didj_update_bootloader <path>

CAUTION:
!!Attempts to flash firmware, could potentially be harmful.!!
!!Make sure Battery's are Fresh, or A/C adpater is used!!

Update Didj bootloader. Files must be in bootloader-LF_LF1000 directory.
Searches from the current local directory for the top level directory of the firmware, local path can be directly inside the top level directory or one above it.
MD5 files will be created automatically.
        """        
        try:
            self.is_remote(self._didj_client)
            abspath = self.get_abspath(s)
            self._didj_client.upload_bootloader(abspath)
            if not self.debug:                
                self._didj_client.eject()
                self.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_didj_update_cleanup(self, s):
        """
Usage:
    didj_update_cleaup

Remove Didj firmware and bootloader from device.
        """
        try:
            self.is_remote(self._didj_client)
            self._didj_client.cleanup()
        except Exception, e:
            self.perror(e)

#######################
# DFTP Internal Functions
# clients.dftp
#######################

    def complete_dftp_update(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)



    def get_version(self):
        try:
            return '%s' % self._dftp_client.version_number
        except Exception, e:
            self.error(e)



    def dftp_device_info(self):
        try:
            print 'Device:\t\t\t%s' % self._dftp_client.get_device_name()
            print 'Firmware Version:\t%s' % self._dftp_client.firmware_version
            print 'Board ID:\t\t%s' % self._dftp_client.get_board_id()
            print 'Device IP:\t\t%s' % self._remote_conn.device_id
            print 'Host IP:\t\t%s' % self._remote_conn.host_id
            print 'DFTP Version: \t\t%s' % self._dftp_client.dftp_version
        except Exception, e:
            self.error(e)



    def send(self, cmd):
        try:
            print self._dftp_client.sendrtn(cmd)
        except Exception, e:
            self.error(e)

#######################
# DFTP User Functions
# clients.dftp
#######################

    def do_dftp_connect(self, s):
        """
Usage:
    dftp_connect

Connect to device for dftp session.
Will attempt to configure IPs as needed.
This could take a minute or so, if you just booted the device.
        """
        try:
            if not self.is_remote(self._dftp_client, True):
                nc = conn_iface(net_connection(self.host_id, self.device_id, self.debug))
                self._dftp_client = dftp_client(nc, self.debug)
                self.remote_connection_init(nc, fs_iface(self._dftp_client), self._dftp_client)
                self._dftp_client.create_client()
                self.remote_path_init()
                self.dftp_device_info()
            else:
                self.error('DFTP client already running')
        except Exception, e:
            self.perror(e)



    def do_dftp_disconnect(self, s):
        """
Usage:
    dftp_disconnect

Disconnect DFTP client.
This will cause the DFTP server to start announcing its IP again, except Explorer's surgeon.cbf version, which will reboot the device
        """
        try:
            self.is_remote(self._dftp_client)
            self._dftp_client.disconnect()
            self._dftp_client = None
            self.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_dftp_server_version(self, s):
        """
Usage
    dftp_server_version <number>

Sets the version number of the dftp server.
OpenLFConnect checks for version 1.12 for surgeon running before a firmware update.
Set this to 1.12 if getting complaints, or surgeon has its dftp version updated.
    """
        try:
            self.is_remote(self._dftp_client)
            if s != '':
                self._dftp_client.dftp_version = s
            else:
                print 'No number selected'
        except Exception, e:
            self.perror(e)



    def do_set_firmware_version(self, s):
        """
Usage:
    set_firmware_version <number>

Manually configure firmware version, useful if you've mixed and matched device firmware, or changed version numbers.
Mostly used for update firmware style.
1.x.x.x = Explorer
2.x.x.x = LeapPad
        """
        try:
            self.is_remote(self._dftp_client)
            if s != '':
                self._dftp_client.version_number = s
            else:
                print 'No number selected'
        except Exception, e:
            self.perror(e)


    def do_dftp_device_info(self, s):
        """
Usage:
    dftp_device_info

Returns the device name, LeapPad or Explorer if determined, and the firmware revision.
Note: the firmware revision is accurate, device is guessed from it.
1.x.x.x = Explorer
2.x.x.x = LeapPad
        """
        try:
            self.is_remote(self._dftp_client)
            self.dftp_device_info()
        except Exception, e:
            self.perror(e)



    def do_dftp_update(self, s):
        """
Usage:
    update <local path>

CAUTION:
!!Attempts to flash firmware, could potentially be harmful.!!
!!Make sure Battery's are Fresh, or A/C adpater is used!!

Uploads and flashes to NAND the files in <local path>.
Note: Files must conform to LF naming conventions. Explorer in a Firmware-Base/* directory, LeapPad in firmware/sd/*
Searches from the current local directory for the top level directory of the firmware, local path can be directly inside the top level directory or one above it.
What firmware it to tries to upload depends on version number.
1.x.x.x = Explorer
2.x.x.x = LeapPad

Caution: Has not been tested on LeapPad, theoretically it should work though, please confirm to author yes or no if you get the chance.
        """
        try:
            self.is_remote(self._dftp_client)
            remote = self._remote_set
            
            if remote:
                self.set_local()
            
            path = self.get_abspath(s)
            
            if self._fs.is_dir(path):
                self._dftp_client.update_firmware(path)
            else:
                self.error('Path is not a directory.')

        except Exception, e:
            self.perror(e)


    
    def do_dftp_reboot(self, s):
        """
Usage:
    update_reboot

After running update, run this to trigger a reboot
        """
        try:
            self.is_remote(self._dftp_client)
            self._dftp_client.update_reboot()
            self._dftp_client.disconnect()
            self._dftp_client = None
            self.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_send(self, s):
        """
Usage:
    send <raw command>

Advanced use only, don't know, probably shouldn't.
        """
        try:
            self.is_remote(self._dftp_client)
            self.send(s)
        except Exception, e:
            self.perror(e)

#######################
# Pager Internal Functions
# clients.pager
#######################    

    def complete_boot_surgeon(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)

#######################
# Pager User Functions
# clients.pager
#######################

    def do_boot_surgeon(self, s):
        """
Usage:
    boot_surgeon <path to surgeon.cbf>

Uploads a Surgeon.cbf file to a device in USB Boot mode. 
File can be any name, but must conform to CBF standards.
        """
        try:
            self._pager_client = pager_client(self.debug)
            abspath = self.get_abspath(s)

            if not self._fs.is_dir(abspath):
                self._pager_client = pager_client(mount_connection())
                self._pager_client.upload_firmware(abspath)
                self._pager_client = None
            else:
                self.error('Path is not a file.')

            self._pager_client = None
        except Exception, e:
            self.perror(e)

#######################
# UI Internal Functions
# OpenLFConnect
#######################

    def complete_ls(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)



    def complete_cd(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)



    def complete_mkdir(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)



    def complete_rmdir(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)



    def complete_rm(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)

#######################
# UI User Functions
# OpenLFConnect
#######################

    def do_remote(self, s):
        """
Usage:
    remote

Set to remote device for filesystem navigation.
        """
        try:
            self.is_remote()
            self.set_remote()
        except Exception, e:
            self.perror(e)


        
    def do_local(self, s):
        """
Usage:
    local

Set to prompt to local host for filesystem navigation.
        """
        try:
            self.set_local()
        except Exception, e:
            self.perror(e)



    def do_cwdr(self, s):
        """
Usage:
    cwdr

Print current remote directory path.
        """
        print self._remote_path



    def do_cwdl(self, s):
        """
Usage:
    cwdl

Print current local directory path.
        """
        print self._local_path



    def do_exit(self, s):
        """
Usage:
    exit

Exit OpenLFConnect
        """
        sys.exit(0)



    def do_ls(self, s):
        """
Usage:
    ls [path]

List directory contents. Where depends on which is set, remote or local
        """            
        try:
            abspath = self.get_abspath(s)
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
        except Exception, e:
            self.perror(e)




    def do_cd(self, s):
        """
Usage:
    cd <path>

Change directories. Where depends on which is set, remote or local
        """
        try:
            self.is_empty(s)
            abspath = self.get_abspath(s)
            self.set_path(abspath)
        except Exception, e:
            self.perror(e)



    def do_mkdir(self, s):
        """
Usage:
    mkdir <path>

Create directory. Where depends on which is set, remote or local
        """
        try:
            self.is_empty(s)                
            abspath = self.get_abspath(s)
            
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                self._fs.mkdir(abspath)

        except Exception, e:
            self.perror(e)


    
    def do_rmdir(self, s):
        """
Usage:
    rmd <path>

Delete directory. Where depends on which is set, remote or local
        """
        try:
            self.is_empty(s)                
            abspath = self.get_abspath(s)
            
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                self._fs.rmdir(abspath)
                
        except Exception, e:
            self.perror(e)



    def do_rm(self, s):
        """
Usage:
    rm <file>

Delete file. Where depends on which is set, remote or local
        """
        try:
            self.is_empty(s)                
            abspath = self.get_abspath(s)
            
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                self._fs.rm(abspath)

        except Exception, e:
            self.perror(e)

#######################
# UI Up/Download Internal Functions
# OpenLFConnect
# Requires Connection to device
#######################

    def complete_download(self, text, line, begidx, endidx):
        return self.complete_remote(text, line, begidx, endidx)
    
    def complete_download_dir(self, text, line, begidx, endidx):
        return self.complete_remote(text, line, begidx, endidx)
    
    def complete_upload(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)
    
    def complete_upload_dir(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)

    def complete_cat(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)

#######################
# UI Up/Download User Functions
# OpenLFConnect
# Requires Connection to device
#######################

    def do_upload(self, s):
        """
Usage:
    upload <local file>

Upload the specified local file to the current remote directory, Will overwrite with out prompt.
        """
        try:
            self.is_remote()
            self.is_empty(s)
            remote = self._remote_set
            
            if remote:
                self.set_local()
                
            abspath = self.get_abspath(s)
            self.set_remote()
            remote_path = os.path.join(self._path, os.path.basename(abspath))

            if sys.platform == 'win32':
                remote_path = remote_path.replace('\\', '/')
            
            self._fs.upload_file(abspath, remote_path)
            
            if not remote:
                self.set_local()
                    
        except Exception, e:
            #if not remote:
                #self.set_local()
            self.perror(e)




    def do_upload_dir(self, s):
        """
Usage:
    upload_dir <local directory>

Upload the specified local directory into the current remote directory, Will overwrite with out prompt.
        """
        try:
            self.is_remote()
            self.is_empty(s)
            remote = self._remote_set
            
            if remote:
                self.set_local()
                
            abspath = self.get_abspath(s)
            self.set_remote()
            remote_path = os.path.join(self._path, os.path.basename(abspath))

            if sys.platform == 'win32':
                remote_path = remote_path.replace('\\', '/')
            
            self._fs.upload_dir(abspath, remote_path)
            
            if not remote:
                self.set_local()

        except Exception, e:
            if not remote:
                self.set_local()
            self.perror(e)



    def do_download(self, s):
        """
Usage:
    download <remote file>

Download the specified remote file to the current local directory, will over write with out prompt.
        """
        try:
            self.is_remote() 
            self.is_empty(s) 
            remote = self._remote_set
            
            if not remote:
                self.set_remote()
                
            abspath = self.get_abspath(s)
            
            self._fs.download_file(os.path.join(self._local_path, os.path.basename(abspath)), abspath)
            
            if not remote:
                self.set_local()

        except Exception, e:
            if not remote:
                self.set_local()
            self.perror(e)



    def do_download_dir(self, s):
        """
Usage:
    download_dir <remote directory>

Download the specified remote directory into the current local directory, will over write with out prompt.
        """
        try:
            self.is_remote() 
            self.is_empty(s)   
            remote = self._remote_set
            
            if not remote:
                self.set_remote()
                
            abspath = self.get_abspath(s)

            self._fs.download_dir(os.path.join(self._local_path, os.path.basename(abspath)), abspath)
            if not remote:
                self.set_local()

        except Exception, e:
            if not remote:
                self.set_local()
            self.perror(e)


    def do_cat(self, s):
        """
Usage:
    cat <path>

Prints the contents of a file to the screen.
Doesn't care what kind or how big of a file.
        """
        try:
            self.is_empty(s)

            abspath = self.get_abspath(s)
            print self._fs.cat(abspath)
        except Exception, e:
            self.perror(e)

#######################
# UI Convenience Functions
# OpenLFConnect
# No Rules Below, Whatever goes goes.
#######################

    def do_enable_sshd(self, s):
        """
Usage:
    enable_sshd
    
Uploads two custom files, to enable the ssh server on boot, files found in <app path>/files/[LX|Lpad]/sshd_enable/.
After uploaded, after first reboot of the device, give it a minute to generate the keys before trying to connect.
Username:root
Password:<blank>

Caution: Has not been tested on LeapPad, theoretically it should work though, please confirm to author yes or no if you get the chance.
        """
        try:
            self.is_remote()
            remote = self._remote_set
            
            if not remote:
                self.set_remote()
                
            vn = self._dftp_client.board_id()
            
            if vn.split('.')[0] == '1':
                self._fs.upload_file('files/LX/enable_sshd/rcS', '/etc/init.d/rcS')
                self._fs.upload_file('files/LX/enable_sshd/sshd_config', '/etc/ssh/sshd_config')
            elif vn.split('.')[0] == '2':
                self._fs.upload_file('files/Lpad/enable_sshd/rcS', '/etc/init.d/rcS')
                self._fs.upload_file('files/Lpad/enable_sshd/sshd_config', '/etc/ssh/sshd_config')
            else:
                self.error('Could not determine device: Firmware version: %s' % vn)
                
            if not remote:
                self.set_local()
        except Exception, e:
            if not remote:
                self.set_local()
            self.perror(e)



if __name__ == '__main__':

    OpenLFConnect().cmdloop()
        
