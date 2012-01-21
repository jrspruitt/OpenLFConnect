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

from services.networking import config as netconfig
from services.pager import pager
from services.dftp import client as dftpclient
from services.local import client as localclient
from services.didj import client as didjclient
from services.local import config as localconfig

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

        self._dftp = None
        self._didj = None
        self._pager = None
        self._local_fs = localclient(self.debug)

        self._remote_path_client = None
        self._remote_path_config = None        
        self._local_path_client = self._local_fs
        self._path_module = self._local_path_client
        
        self._remote_type = None
        self._remote_set = False
        
        self._local_path_init = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files')).replace('\\', '/')
        self._local_path = self._local_path_init
        self._remote_path_init = '/'
        self._remote_path = self._remote_path_init
        
        self._path = ''
        
        self._remote_path_dir_list = []
        self._local_path_dir_list = []
        self._path_dir_list = []

        self._host_ip = ''
        self._device_ip = ''
        self._dev_id = ''
        self._mount_point = ''
        
        self.set_local_path(self._local_path)



#######################
# OpenLFConnect.py
# Internal Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def perror(self, e):
        print '%s' % e



# Remote/Local Client Functions

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



    def set_remote(self):
        self._path_dir_list = self._remote_path_dir_list
        self._path_module = self._remote_path_client
        self._path = self._remote_path
        self._remote_set = True
        self.prompt = 'remote%s' % self._prompt_suffix



    def set_local(self):
        if self._local_path_client:
            self._path_dir_list = self._local_path_dir_list
            self._path_module = self._local_path_client
            self._path = self._local_path
            self._remote_set = False
            self.prompt = 'local%s' % self._prompt_suffix
        else:
            self.error('No local client running.')



    def is_remote(self, rmod=False, ret_bool=False):
        error = ''
        connected = False
        
        if rmod is None:
            rmod = True

        if not self._remote_path_config:
            error = 'No connection established.'            
        else:
            connected = self._remote_path_config.is_connected()

            if not connected:
                self.remote_destroy()
                self.error('Device not connected')
    
            elif connected and rmod is False:
                return True
                
            elif connected and rmod is not self._remote_path_client:
                self.error('Device connected, but wrong client is running.')
                
            elif connected and rmod is self._remote_path_client:
                return True
                
            else:
                self.remote_destroy()
                self.error('Something is wrong with your connection.')

        if ret_bool:
            return False
        else:
            self.error(error)
        


    def remote_config_init(self, config, client, rtype):
        self._remote_path_config = config
        self._remote_type = rtype
        self._remote_path_client = client



    def remote_path_init(self):
        if self._remote_type == 'network':
            self.set_remote_path(self._remote_path)
        elif self._remote_type == 'mount':
            self.set_remote_path(self._remote_path_config.mount_point)
        else:
            self.set_local()
            self.error('No remote module present.')
 
 
 
    def remote_destroy(self):
        self._dftp = None
        self._didj = None
        self._didj_client = None
        self._remote_path_config = None
        self._remote_type = None
        self._remote_path_client = None
        self._remote_set = False
        self._remote_path = self._remote_path_init
        self.set_local()
        self.set_local_path(self._local_path_init)


# Path Functions
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



    def get_path_prefix(self):
        if sys.platform == 'win32' and not self._remote_set:
            return '%s/' % os.path.splitdrive(self._local_path)[0]
        elif sys.platform == 'linux2':
            return '/'
        else:
            return '/'



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



    def set_path(self, path):
        if self._remote_set:
            
            if self._path_module.is_dir(path):
                self.set_remote_path('%s' % path)
            else:
                self.error('Is not a directory')
        else:
            
            if self._local_path_client.is_dir(path):
                self.set_local_path('%s' % path)
            else:
                self.error('Is not a directory')



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
        if self._dftp:
            self._dftp.debug = self.debug
        if self._didj:
            self._didj.debug = self.debug
        if self._remote_path_config:
            self._remote_path_config.debug = self.debug
        if self._local_fs:
            self._local_fs.debug = self.debug
        if self._pager:
            self._pager.debug = self.debug

 
    def do_debug_off(self, s):
        """
Usage:
    debug_off

Turns off debugging mode. Updates will be attempted.
        """
        self.debug = False
        if self._local_path_client:
            self._local_path_client.debug = self.debug
        if self._remote_path_client:
            self._remote_path_client.debug = self.debug



    def do_is_connected(self):
        if self._remote_path_config and self._remote_path_config.is_connected():
            print 'Device is connected' 
        else:
            self.perror('Device not connected')



#######################
# local.py
#######################

    def do_set_dev_id(self, s):
        """
Usage:
    set_dev_id <device id>

Manually configures the device id, in Linux its the generic scsi
device file, ex. /dev/sg2 or harddrive /dev/sdb , in windows its the PhysicalDrive ex. PD1.
This needs to be set before attempting to connect or set up a network connection.
This is only needed if for some reason, OpenLFConnect can not determine it.
        """
        if s == '':
            self.error('No device ID selected.')
        self._dev_id = s



    def do_get_dev_id(self, s):
        """
Usage:
    get_dev_id

Returns the currently configured device id.
        """
        try:
            if self._remote_type == 'mount' and self.is_remote(None, True):
                print self._remote_path_config.dev_id
            else:
                self.error('Mounted remote client not running.')
        except Exception, e:
            self.perror(e)



    def do_set_mount_point(self, s):
        """
Usage:
    set_mount_point <mount point>

Manually configure the mount point, ex. Linux /media/didj, ex. Windows D:\
This needs to be set before a attempting to connect to or mount the device.
This is only needed if for some reason, OpenLFConnect can not determine it.
        """
        if s == '':
            self.error('No mount point selected.')

        self._mount_point = s



    def do_get_mount_point(self, s):
        """
Usage:
    get_mount_point

Returns the currently configured mount point.
        """
        try:
            if self._remote_type == 'mount' and self.is_remote(None, True):
                print self._remote_path_config.mount_point
            else:
                self.error('Mounted remote client not running.')
        except Exception, e:
            self.perror(e)



#######################
# didj.py
# Internal Functions
#######################

    def complete_didj_update_bootloader(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)



    def complete_didj_update(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)



    def complete_didj_update_firmware(self, text, line, begidx, endidx):
        return self.path_complete_local(text, line, begidx, endidx)



#######################
# didj.py
# User Functions
#######################

    def do_didj_mount(self, s):
        """
Usage:
    didj_mount [mount name]

Unlock Didj to allow it to mount on host system.
        """
        try:
            if not self.is_remote(None, True) and self._remote_type != 'mount':
                lc = localconfig(self._dev_id, self._mount_point, self.debug)
                self._didj_client = localclient(self.debug)
                self.remote_config_init(lc, self._didj_client, 'mount')
                self._didj = didjclient(lc, self.debug)
                
                self._didj.mount()
                self.remote_path_init()
                print 'Mounted on: %s' % self._remote_path_config.mount_point
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
            self._didj.umount()
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
            self._didj.eject()
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
            self._didj.upload_firmware(abspath)
            self._didj.upload_bootloader(abspath)
            if not self.debug:      
                self._didj.eject()
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
            self._didj.upload_firmware(abspath)
            if not self.debug:                
                self._didj.eject()
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
            self._didj.upload_bootloader(abspath)
            if not self.debug:                
                self._didj.eject()
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
            self._didj.cleanup()
        except Exception, e:
            self.perror(e)



#######################
# networking.py
#######################

    def config_ip(self):        
        try:
            self._remote_path_config.config_ip()
        except Exception, e:
            self._remote_path_config = None
            self.error(e)


    def do_config_ip(self, s):
        """
Usage:
    config_ip

Gets the IP addresses of the Device and Host, and if on Windows, sets the necessary Route to establish connectivity.
This could take a minute or so, if you just booted the device.
        """
        try:
            self.config_ip()
            self.do_ip(None)
        except Exception, e:
            self.perror(e)




    def do_ip(self, s):
        """
Usage:
    ip [host|device]

Returns the assigned IP address or both.
        """
        try:
            hip = self.do_get_host_ip(None)
            dip = self.do_get_device_ip(None)
            
            if not hip:
                hip = 'Not Set'
                
            if not dip:
                dip = 'Not Set'
    
            if s == 'host':
                print '%s' % hip
            elif s == 'device':
                print '%s' % dip
            else:
                print 'Host:\t\t%s' % hip
                print 'Device:\t\t%s' % dip
        except Exception, e:
            self.perror(e)



    def get_device_ip(self):
        """
Usage:
    get_device_ip

Returns currently configured device IP.
        """
        try:
            if self._remote_type == 'network' and self.is_remote(None, True):
                print self._remote_path_config.host_ip
            else:
                self.error('Networked remote client not running.')
        except Exception, e:
            self.perror(e)



    def do_set_device_ip(self, s):
        """
Usage:
    set_device_ip <IP>

Manually set the device's IP to a known value, this will not reconfigure the devices's IP, should be set to it's actual IP.
This should be set before connecting to a device, or establishing a network connection.
        """
        if s == '':
            self.error('No IP selected.')

        self._device_ip = s



    def do_get_host_ip(self):
        """
Usage:
    get_host_ip

Returns currently configured host IP.
        """
        try:
            if self._remote_type == 'network' and self.is_remote(None, True):
                print self._remote_path_config.host_ip
            else:
                self.error('Networked remote client not running.')
        except Exception, e:
            self.perror(e)



    def do_set_host_ip(self, s):
        """
Usage:
    set_host_ip <IP>

Manually set the host's IP to a known value, this will not reconfigure the host's IP, should be set to it's actual IP.
This should be set before connecting to a device, or establishing a network connection.
        """
        if s == '':
            self.error('No IP selected.')
            
        self._host_ip = s



#######################
# dftp.py
# Internal Functions
#######################



    def complete_dftp_update(self, text, line, begidx, endidx):
        return self.complete_local(text, line, begidx, endidx)




    def get_version(self):
        try:
            return '%s' % self._dftp.version_number
        except Exception, e:
            self.error(e)


    def dftp_device_info(self):
        try:
            print 'Device:\t\t\t%s' % self._dftp.get_device_name()
            print 'Firmware Version:\t%s' % self._dftp.firmware_version
            print 'Board ID:\t\t%s' % self._dftp.get_board_id()
            print 'Device IP:\t\t%s' % self._remote_path_config.device_ip
            print 'Host IP:\t\t%s' % self._remote_path_config.host_ip
            print 'DFTP Version: \t\t%s' % self._dftp.dftp_version
        except Exception, e:
            self.error(e)



    def send(self, cmd):
        try:
            print self._dftp.sendrtn(cmd)
        except Exception, e:
            self.error(e)



#######################
# dftp.py
# User Functions
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
            if not self.is_remote(self._dftp, True):
                nc = netconfig(self._host_ip, self._device_ip, self.debug)
                self.remote_config_init(nc, dftpclient(nc, self.debug), 'network')
                self._dftp = self._remote_path_client
                self._dftp.create_client()
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
            self.is_remote(self._dftp)
            self._dftp.disconnect()
            self._dftp = None
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
            self.is_remote(self._dftp)
            if s != '':
                self._dftp.dftp_version = s
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
            self.is_remote(self._dftp)
            if s != '':
                self._dftp.version_number = s
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
            self.is_remote(self._dftp)
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
            self.is_remote(self._dftp)
            remote = self._remote_set
            
            if remote:
                self.set_local()
            
            path = self.get_abspath(s)
            
            if self._path_module.is_dir(path):
                self._dftp.update_firmware(path)
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
            self.is_remote(self._dftp)
            self._dftp.update_reboot()
            self._dftp.disconnect()
            self._dftp = None
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
            self.is_remote(self._dftp)
            self.send(s)
        except Exception, e:
            self.perror(e)



#######################
# pager.py
#######################    

    def complete_boot_surgeon(self, text, line, begidx, endidx):
        return self.complete_path(text, line, begidx, endidx)



    def do_boot_surgeon(self, s):
        """
Usage:
    boot_surgeon <path to surgeon.cbf>

Uploads a Surgeon.cbf file to a device in USB Boot mode. 
File can be any name, but must conform to CBF standards.
        """
        try:
            self._pager = pager(self.debug)
            abspath = self.get_abspath(s)

            if not self._path_module.is_dir(abspath):
                self._pager = pager(localconfig())
                self._pager.upload_firmware(abspath)
                self._pager = None
            else:
                self.error('Path is not a file.')

            self._pager = None
        except Exception, e:
            self.perror(e)



#######################
# Module independant
# Filesystem commands
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




    def do_cd(self, s):
        """
Usage:
    cd <path>

Change directories. Where depends on which is set, remote or local
        """
        try:
            if s == '':
                self.error('No path set.')
            abspath = self.get_abspath(s)
            if self._path_module.is_dir(abspath):
                self.set_path(abspath)
            else:
                print 'Path is not in a directory'
        except Exception, e:
            self.perror(e)



    def do_mkdir(self, s):
        """
Usage:
    mkdir <path>

Create directory. Where depends on which is set, remote or local
        """
        try:
            if s == '':
                self.error('No path set.')
                
            abspath = self.get_abspath(s)
            
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                
                if self._path_module.is_dir(os.path.dirname(abspath)):
                    self._path_module.mkdir(abspath)
                else:
                    print 'Path is not in a directory'
        except Exception, e:
            self.perror(e)


    
    def do_rmdir(self, s):
        """
Usage:
    rmd <path>

Delete directory. Where depends on which is set, remote or local
        """
        try:
            if s == '':
                self.error('No path set.')
                
            abspath = self.get_abspath(s)
            
            if abspath == self.get_path_prefix():
                self.error('No directory selected.')
            else:
                
                if self._path_module.is_dir(os.path.dirname(abspath)):
                    self._path_module.rmdir(abspath)
                else:
                    print 'Path is not in a directory'
        except Exception, e:
            self.perror(e)



    def do_rm(self, s):
        """
Usage:
    rm <file>

Delete file. Where depends on which is set, remote or local
        """
        try:
            if s == '':
                self.error('No path set.')
                
            abspath = self.get_abspath(s)
            
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
# Remote Device
# Upload/Download Commands
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




    def do_upload(self, s):
        """
Usage:
    upload <local file>

Upload the specified local file to the current remote directory, Will overwrite with out prompt.
        """
        try:
            self.is_remote()
            
            if s == '':
                self.error('No path set.')
                
            remote = self._remote_set
            
            if remote:
                self.set_local()
                
            abspath = self.get_abspath(s)
            
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




    def do_upload_dir(self, s):
        """
Usage:
    upload_dir <local directory>

Upload the specified local directory into the current remote directory, Will overwrite with out prompt.
        """
        try:
            self.is_remote()
            
            if s == '':
                self.error('No path set.')
                
            remote = self._remote_set
            
            if remote:
                self.set_local()
                
            abspath = self.get_abspath(s)
            
            if self._path_module.is_dir(abspath):
                self.set_remote()
                
                remote_path = os.path.join(self._path, os.path.basename(abspath))

                if sys.platform == 'win32':
                    remote_path = remote_path.replace('\\', '/')
                
                self._path_module.upload_dir(abspath, remote_path)
                
                if not remote:
                    self.set_local()
            else:
                self.error('Path not set to a directory.')
        except Exception, e:
            self.perror(e)



    def do_download(self, s):
        """
Usage:
    download <remote file>

Download the specified remote file to the current local directory, will over write with out prompt.
        """
        try:
            self.is_remote() 
            if s == '':
                self.error('No path set.')
                
            remote = self._remote_set
            
            if not remote:
                self.set_remote()
                
            abspath = self.get_abspath(s)
            
            if not self._path_module.is_dir(abspath):
                self._path_module.download_file(os.path.join(self._local_path, os.path.basename(abspath)), abspath)
                if not remote:
                    self.set_local()
            else:
                self.error('Path not set to a file.')

        except Exception, e:
            self.perror(e)



    def do_download_dir(self, s):
        """
Usage:
    download_dir <remote directory>

Download the specified remote directory into the current local directory, will over write with out prompt.
        """
        try:
            self.is_remote() 
            if s == '':
                self.error('No path set.')
                
            remote = self._remote_set
            
            if not remote:
                self.set_remote()
                
            abspath = self.get_abspath(s)
            
            if self._path_module.is_dir(abspath):
                self._path_module.download_dir(os.path.join(self._local_path, os.path.basename(abspath)), abspath)
                if not remote:
                    self.set_local()
            else:
                self.error('Path not set to a directory.')

        except Exception, e:
            self.perror(e)


    def do_cat(self, s):
        """
Usage:
    cat <path>

Prints the contents of a file to the screen.
Doesn't care what kind or how big of a file.
        """
        try:
            if s == '':
                self.error('No path selected.')

            abspath = self.get_abspath(s)
            if not self._path_module.is_dir(abspath):
                print self._path_module.cat(abspath)
            else:
                self.error('Path not set to a file')
        except Exception, e:
            self.perror(e)



#######################
# Convenience Functions
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
                
            vn = self._dftp.board_id()
            
            if vn.split('.')[0] == '1':
                self._path_module.upload_file('files/LX/enable_sshd/rcS', '/etc/init.d/rcS')
                self._path_module.upload_file('files/LX/enable_sshd/sshd_config', '/etc/ssh/sshd_config')
            elif vn.split('.')[0] == '2':
                self._path_module.upload_file('files/Lpad/enable_sshd/rcS', '/etc/init.d/rcS')
                self._path_module.upload_file('files/Lpad/enable_sshd/sshd_config', '/etc/ssh/sshd_config')
            else:
                self.error('Could not determine device: Firmware version: %s' % vn)
                
            if not remote:
                self.set_local()
        except Exception, e:
            self.perror(e)



if __name__ == '__main__':

    OpenLFConnect().cmdloop()
        
