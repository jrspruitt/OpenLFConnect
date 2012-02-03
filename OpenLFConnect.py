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
# OpenLFConnect.py Version 0.7.1
import os
import cmd
import sys
import shlex

from olcmodules.location import manager as loc_manager
from olcmodules import config

from olcmodules.system.networking import connection as net_connection
from olcmodules.system.mount import connection as mount_connection
from olcmodules.system.interface import config as conn_iface

from olcmodules.clients.pager import client as pager_client
from olcmodules.clients.dftp import client as dftp_client
from olcmodules.clients.didj import client as didj_client
from olcmodules.clients.local import client as local_client
from olcmodules.clients.interface import filesystem as fs_iface

from olcmodules.firmware import cbf, packages
from olcmodules.firmware.images import ubi, jffs2


class OpenLFConnect(cmd.Cmd, object):
    def __init__(self):
        cmd.Cmd.__init__(self)
        print 'OpenLFConnect Version 0.7.1'
        self.debug = False        
        
        self._init_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files')).replace('\\', '/')
        self._lm = loc_manager(self._init_path, cmd.Cmd)
        
        self._dftp_client = None
        self._didj_client = None
        self._pager_client = None

        self._host_id = ''
        self._device_id = ''
        
        self._lm.set_local(self._lm.local_path)
        
        config.olc_files_dirs_check()
        
##############################################################################
# OpenLFConnect.py
# Internal Functions
#######################

    def error(self, e):
        assert False, '%s' % e

    def perror(self, e):
        print '%s' % e

    def emptyline(self):
        pass
#######################
# Internal User Connection/Client Config Functions
# OpenLFConnect
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

##############################################################################
# Didj Internal Functions
# clients.didj
#######################

    def complete_didj_update_bootloader(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_didj_update(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_didj_update_firmware(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)


    def didj_device_info(self):
        try:
            print '  Device Name:\t\tDidj'
            print '  Serial Number:\t%s' % self._didj_client.serial_number
            print '  Battery Level:\t%s' % self._didj_client.battery_level
            print '  Needs Repair:\t\t%s' % self._didj_client.needs_repair
            print '  Device ID:\t\t%s' % self._lm.remote_conn.device_id
            print '  Mount Point:\t\t%s' % self._lm.remote_conn.host_id
        except Exception, e:
            self.error(e)
            
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
            if not self._lm.is_client(self._didj_client):
                try:
                    mc = conn_iface(mount_connection(self.device_id, self.host_id, self.debug))
                    self._didj_client = didj_client(mc, self.debug)                
                    self._lm.remote_connection_init(mc, fs_iface(local_client(self.debug)), self._didj_client)
                    self._didj_client.mount()
                    self._lm.remote_path_init()
                    self.didj_device_info()
                except Exception, e:
                    self._didj_client = None
                    self._lm.remote_destroy()
                    self.error(e)                    
            else:
                self.perror('Didj is already running.')
        except Exception, e:
            self.perror(e)



    def do_didj_eject(self, s):
        """
Usage:
    didj_eject

Eject the Didj which will unmount on host system, if the firmware updates are 
on the Didj, an update will be triggered. If they are not, it will ask you to unplug it.
Could take some time to unmount and eject if you have written files to the device.
        """
        try:
            self._lm.is_remote(self._didj_client)
            self._didj_client.eject()
            self._lm.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_didj_device_info(self, s):
        """
Usage:
    didj_device_info

Returns various information about device and mount.
        """
        try:
            self._lm.is_remote(self._didj_client)
            self.didj_device_info()
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
            self._lm.is_remote(self._didj_client)
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            self._didj_client.upload_firmware(abspath)
            self._didj_client.upload_bootloader(abspath)
            if not self.debug:      
                self._didj_client.eject()
                self._lm.last_location()
                self._lm.remote_destroy()
            else:
                self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
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
            self._lm.is_remote(self._didj_client)
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            self._didj_client.upload_firmware(abspath)
            if not self.debug:                
                self._didj_client.eject()
                self._lm.last_location()
                self._lm.remote_destroy()
            else:
                self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
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
            self._lm.is_remote(self._didj_client)
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            self._didj_client.upload_bootloader(abspath)
            if not self.debug:                
                self._didj_client.eject()
                self._lm.last_location()
                self._lm.remote_destroy()
            else:
                self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_didj_update_cleanup(self, s):
        """
Usage:
    didj_update_cleaup

Remove Didj firmware and bootloader from device.
        """
        try:
            self._lm.is_remote(self._didj_client)
            self._didj_client.cleanup()
        except Exception, e:
            self.perror(e)

##############################################################################
# DFTP Internal Functions
# clients.dftp
#######################

    def complete_dftp_update(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)


    def dftp_device_info(self):
        try:
            device_name = self._dftp_client.device_name
            serial = self._dftp_client.serial_number
            print '  Device:\t\t%s' % device_name
            print '  Firmware Version:\t%s' % self._dftp_client.firmware_version
            print '  Serial Number\t\t%s' % serial
            print '  Board ID:\t\t%s' % self._dftp_client.board_id
            print '  Battery Level\t\t%s' % self._dftp_client.battery_level
            print '  Device IP:\t\t%s' % self._lm.remote_conn.device_id
            print '  Host IP:\t\t%s' % self._lm.remote_conn.host_id
            print '  Host Name:\t\t%s-%s' % (device_name, serial)
            print '  DFTP Version:\t\t%s' % self._dftp_client.dftp_version
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
            if not self._lm.is_client(self._dftp_client):
                try:
                    nc = conn_iface(net_connection(self.host_id, self.device_id, self.debug))
                    self._dftp_client = dftp_client(nc, self.debug)
                    self._lm.remote_connection_init(nc, fs_iface(self._dftp_client), self._dftp_client)
                    self._dftp_client.create_client()
                    self._lm.remote_path_init()
                    self.dftp_device_info()
                except Exception, e:
                    self._dftp_client = None
                    self._lm.remote_destroy() 
                    self.error(e)                   
            else:
                self.perror('DFTP client already running')
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
            self._lm.is_remote(self._dftp_client)
            self._dftp_client.disconnect()
            self._dftp_client = None
            self._lm.remote_destroy()
        except Exception, e:
            self.perror(e)



    def do_dftp_server_version(self, s):
        """
Usage
    dftp_server_version [number]

Sets the version number of the dftp server. Or retrieves if none specified
OpenLFConnect checks for version 1.12 for surgeon running before a firmware update.
Set this to 1.12 if getting complaints, or surgeon has its dftp version updated.
    """
        try:
            self._lm.is_remote(self._dftp_client)
            if s != '':
                self._dftp_client.dftp_version = s
            else:
                print self._dftp_client.dftp_version
        except Exception, e:
            self.perror(e)



    def do_dftp_device_info(self, s):
        """
Usage:
    dftp_device_info

Returns various information about the device, and connection.
Note: Device name is guessed from board id.
        """
        try:
            self._lm.is_remote(self._dftp_client)
            self.dftp_device_info()
        except Exception, e:
            self.perror(e)



    def do_dftp_update(self, s):
        """
Usage:
    dftp_update <local path>

CAUTION:
!!Attempts to flash firmware, could potentially be harmful.!!
!!Make sure Battery's are Fresh, or A/C adapter is used!!

Uploads and flashes the files found in path, or the file specified by path.

Caution: Has not been tested on LeapPad, theoretically it should work though, please confirm to author yes or no if you get the chance.
        """
        try:
            self._lm.is_remote(self._dftp_client)
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            self._dftp_client.update_firmware(abspath)
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)


    
    def do_dftp_reboot(self, s):
        """
Usage:
    dftp_reboot

This will trigger a reboot.
        """
        try:
            self._lm.is_remote(self._dftp_client)
            self._dftp_client.reboot()
            self._dftp_client = None
            self._lm.remote_destroy()
        except Exception, e:
            self._dftp_client = None
            self._lm.remote_destroy()
            self.perror(e)



    def do_dftp_reboot_usbmode(self, s):
        """
Usage:
    dftp_reboot_usbmode

This will reboot the device into USB mode, for sending a surgeon.cbf to boot.
If surgeon is booted, will do a standared reboot.
        """
        try:
            self._lm.is_remote(self._dftp_client)
            self._dftp_client.reboot_usbmode()
            self._dftp_client = None
            self._lm.remote_destroy()
        except Exception, e:
            self._dftp_client = None
            self._lm.remote_destroy()
            self.perror(e)


    def do_dftp_mount_patient(self, s):
        """
Usage:
    dftp_mount_patient 0|1|2

Surgeon booted device only. These give you access to the devices filesystem.
0 Unmounts /patient-rfs and /patient-bulk/
1 Mounts /patient-rfs and /patient-bulk/
2 Mounts only /patient-rfs
        """
        try:
            self._lm.is_remote(self._dftp_client)
            self._dftp_client.mount_patient(s)
        except Exception, e:
            self.perror(e)


    def do_dftp_telnet(self, s):
        """
Usage:
    dftp_telnet <start|stop>

Starts or stops the Telnet daemon on the device.
Username:root
Password:<blank>
        """
        try:
            if s in ('start', 'stop'):
                script = os.path.join(config.SCRIPTS_DIR, 'telnet_%s.sh' % s)
                if script:
                    self._lm.is_remote(self._dftp_client)            
                    self._dftp_client.run_script(script)
                    print 'Telnet %s' % s
                else:
                    self.error('The script file seems to be missing.')
            else:
                self.error('Command not recognized.')
        except Exception, e:
            self.perror(e)



    def do_dftp_ftp(self, s):
        """
Usage:
    dftp_ftp <start|stop>

Starts or stops the FTP server on the device.
Username:root
Password:<blank>
        """
        try:
            if s in ('start', 'stop'):
                script = os.path.join(config.SCRIPTS_DIR, 'ftp_%s.sh' % s)
                if script:
                    self._lm.is_remote(self._dftp_client)            
                    self._dftp_client.run_script(script)
                    print 'FTP %s' % s
                else:
                    self.error('The script file seems to be missing.')
            else:
                self.error('Command not recognized.')
        except Exception, e:
            self.perror(e)



    def do_dftp_sshd(self, s):
        """
Usage:
    dftp_sshd <start|stop>

Starts or stops the SSHD daemon on the device. Does not work on surgeon.
Username:root
Password:<blank>
        """
        try:
            if s in ('start', 'stop'):
                script = os.path.join(config.SCRIPTS_DIR, 'sshd_%s.sh' % s)
                if script:
                    self._lm.is_remote(self._dftp_client) 
                    if self._dftp_client.exists_i('/etc/ssh'):           
                        self._dftp_client.run_script(script)
                        print 'SSHD %s' % s
                    else:
                        self.error('SSHD not installed, must be running Surgeon?')
                else:
                    self.error('The script file seems to be missing.')
            else:
                self.error('Command not recognized.')
        except Exception, e:
            self.perror(e)



    def do_dftp_sshd_no_password(self, s):
        """
Usage:
    dftp_sshd_no_password

Patches the sshd_config file to permit login with a blank password.
Should be run before starting sshd, only needs to be done once.
        """
        try:
            script = os.path.join(config.SCRIPTS_DIR, 'sshd_no_password.sh')
            if script:
                self._lm.is_remote(self._dftp_client)
                if self._dftp_client.exists_i('/etc/ssh'):           
                    self._dftp_client.run_script(script)
                    print 'sshd_config patched for empty passwords.'
                else:
                    self.error('SSHD not installed, must be running Surgeon?')
            else:
                self.error('The script file seems to be missing.')
        except Exception, e:
            self.perror(e)



    def do_dftp_run_script(self, s):
        """
Usage:
    dftp_run_script <path>

This takes a shell script as an argument, and proceeds to run it on the device.
Username:root
Password:<blank>
        """
        try:
            self._lm.is_remote(self._dftp_client)
            self._lm.set_local()            
            path = self._lm.get_abspath(s)
            
            self._dftp_client.run_script(path)
                
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_send(self, s):
        """
Usage:
    send <raw command>

Advanced use only, don't know, probably shouldn't.
        """
        try:
            self._lm.is_remote(self._dftp_client)
            self._dftp_client._sock1.settimeout(3)
            self._dftp_client.send('%s\x00' % s)
            ret = self._dftp_client.receive()
            self._dftp_client._sock1.settimeout(1)
            if ret:
                print ret
        except Exception, e:
            self.perror(e)

##############################################################################
# Pager Internal Functions
# clients.pager
#######################    

    def complete_boot_surgeon(self, text, line, begidx, endidx):
        return self._lm.complete_path(text, line, begidx, endidx)

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
            abspath = self._lm.get_abspath(s)

            if not self._lm.fs.is_dir(abspath):
                self._pager_client = pager_client(conn_iface(mount_connection()))
                self._pager_client.upload(abspath)
                print 'Booting surgeon.'
                self._pager_client = None
            else:
                self.error('Path is not a file.')

            self._pager_client = None
        except Exception, e:
            self.perror(e)

##############################################################################
# UI User Complete Internal Functions
# OpenLFConnect
#######################

    def complete_ls(self, text, line, begidx, endidx):
        return self._lm.complete_path(text, line, begidx, endidx)

    def complete_cd(self, text, line, begidx, endidx):
        return self._lm.complete_path(text, line, begidx, endidx)

    def complete_mkdir(self, text, line, begidx, endidx):
        return self._lm.complete_path(text, line, begidx, endidx)

    def complete_rmdir(self, text, line, begidx, endidx):
        return self._lm.complete_path(text, line, begidx, endidx)

    def complete_rm(self, text, line, begidx, endidx):
        return self._lm.complete_path(text, line, begidx, endidx)

    def complete_download(self, text, line, begidx, endidx):
        return self._lm.complete_remote(text, line, begidx, endidx)
    
    def complete_download_dir(self, text, line, begidx, endidx):
        return self._lm.complete_remote(text, line, begidx, endidx)
    
    def complete_upload(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)
    
    def complete_upload_dir(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_cat(self, text, line, begidx, endidx):
        return self._lm.complete_path(text, line, begidx, endidx)


##############################################################################
# OpenLFConnect UI Functions
#######################

#######################
# UI Connection/Client Config Functions
# Debug
# OpenLFConnect
#######################

    def do_debug(self, s):
        """
Usage:
    debug_on

Setting this prevents updates from actually happening, instead printing the files that would have been uploaded.
        """
        if s.lower() in ('on', 'true', 'enable'):
            self.debug = True
        elif s.lower() in ('off', 'false', 'disable'):
            self.debug = False
        else:
            self.perror('Could not determine action from option given.')

        if self._lm.remote_conn:
            self._lm.remote_conn.debug = self.debug
        if self._lm.local_client:
            self._lm.local_client.debug = self.debug
        if self._lm.remote_client:
            self._lm.remote_client.debug = self.debug
        if self._lm.local_fs:
            self._lm.local_fs.debug = self.debug
        if self._lm.remote_fs:
            self._lm.remote_fs.debug = self.debug
                         
#######################
# UI User Connection/Client Config Functions
# Mount
# OpenLFConnect
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

Set the device to use when creating a new mount client.
The device id, in Linux is the generic scsi device file, ex. /dev/sg2 or harddrive /dev/sdb , or Windows the PhysicalDrive ex. PD1.
To reset to auto determine leave input blank.
        """
        if s == '':
            self.device_id = ''
        else:
            self.device_id = s



    def do_get_mount_point(self, s):
        """
Usage:
    get_mount_point

Returns the currently configured mount point to use when creating a new mount client client.
        """
        return self.host_id

    def do_set_mount_point(self, s):
        """
Usage:
    set_mount_point <mount point>

Set the mount point to use when creating a new mount client. 
The mount point, ex. Linux /media/didj, or Windows D:\
To reset to auto determine leave input blank.
        """
        if s == '':
            self.host_id = ''
        else:
            self.host_id = s

#######################
# UI Connection Config Functions
# Networking
# OpenLFConnect
#######################

    def do_get_device_ip(self, s):
        """
Usage:
    get_device_ip

Returns currently configured device IP to use when creating a new network client.
        """
        return self.device_id

    def do_set_device_ip(self, s):
        """
Usage:
    set_device_ip <IP>

Set the device IP address to use when creating a new network client.
ex. 169.254.123.123
To reset to auto determine leave input blank.
        """
        if s == '':
            self.device_id = ''
        else:
            self.device_id = s



    def do_get_host_ip(self, s):
        """
Usage:
    get_host_ip

Returns currently configured host IP to use when creating a new network client.
        """
        return self.host_id

    def do_set_host_ip(self, s):
        """
Usage:
    set_host_ip <IP>

Set the host IP address to use when creating a new network client.
ex. 169.254.123.123
To reset to auto determine leave input blank.
        """
        if s == '':
            self.host_id = ''
        else:
            self.host_id = s
            
#######################
# UI User Location Functions
# OpenLFConnect
#######################

    def do_remote(self, s):
        """
Usage:
    remote

Set to remote device for filesystem navigation.
        """
        try:
            self._lm.is_remote()
            self._lm.set_remote()
        except Exception, e:
            self.perror(e)


        
    def do_local(self, s):
        """
Usage:
    local

Set to prompt to local host for filesystem navigation.
        """
        try:
            self._lm.set_local()
        except Exception, e:
            self.perror(e)
            
#######################
# UI Filesystem Functions
# OpenLFConnect
#######################

    def do_cwdr(self, s):
        """
Usage:
    cwdr

Print current remote directory path.
        """
        print self._lm.remote_path



    def do_cwdl(self, s):
        """
Usage:
    cwdl

Print current local directory path.
        """
        print self._lm.local_path



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
            abspath = self._lm.get_abspath(s)
            dlist = self._lm.get_dir_list(abspath)
            flist = []
            
            for item in dlist:
                
                if item[-1:] == '/':
                    print '  %s' % item
                else:
                    flist.append(item)
                    
            flist.sort(key=str.lower)
            
            for item in flist:
                print '  %s' % item
        except Exception, e:
            self.perror(e)




    def do_cd(self, s):
        """
Usage:
    cd <path>

Change directories. Where depends on which is set, remote or local
        """
        try:
            self._lm.is_empty(s)
            abspath = self._lm.get_abspath(s)
            self._lm.set_path(abspath)
        except Exception, e:
            self.perror(e)



    def do_mkdir(self, s):
        """
Usage:
    mkdir <path>

Create directory. Where depends on which is set, remote or local
        """
        try:
            self._lm.is_empty(s)                
            abspath = self._lm.get_abspath(s)
            
            if abspath == self._lm.get_path_prefix():
                self.error('No directory selected.')
            else:
                self._lm.fs.mkdir(abspath)

        except Exception, e:
            self.perror(e)


    
    def do_rmdir(self, s):
        """
Usage:
    rmd <path>

Delete directory. Where depends on which is set, remote or local
        """
        try:
            self._lm.is_empty(s)                
            abspath = self._lm.get_abspath(s)
            
            if abspath == self._lm.get_path_prefix():
                self.error('No directory selected.')
            else:
                self._lm.fs.rmdir(abspath)
                
        except Exception, e:
            self.perror(e)



    def do_rm(self, s):
        """
Usage:
    rm <file>

Delete file. Where depends on which is set, remote or local
        """
        try:
            self._lm.is_empty(s)                
            abspath = self._lm.get_abspath(s)
            
            if abspath == self._lm.get_path_prefix():
                self.error('No directory selected.')
            else:
                self._lm.fs.rm(abspath)

        except Exception, e:
            self.perror(e)

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
            self._lm.is_remote()
            self._lm.is_empty(s)
            self._lm.set_local()                
            abspath = self._lm.get_abspath(s)
            self._lm.last_location()
            self._lm.set_remote()
            remote_path = os.path.join(self._lm.path, os.path.basename(abspath))

            if sys.platform == 'win32':
                remote_path = remote_path.replace('\\', '/')
            
            self._lm.fs.upload(abspath, remote_path)
            self._lm.last_location()                    
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_download(self, s):
        """
Usage:
    download <remote file>

Download the specified remote file to the current local directory, will over write with out prompt.
        """
        try:
            self._lm.is_remote() 
            self._lm.is_empty(s) 
            self._lm.set_remote()                
            abspath = self._lm.get_abspath(s)            
            self._lm.fs.download(os.path.join(self._lm.local_path, os.path.basename(abspath)), abspath)
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_cat(self, s):
        """
Usage:
    cat <path>

Prints the contents of a file to the screen.
Doesn't care what kind or how big of a file.
        """
        try:
            self._lm.is_empty(s)
            print self._lm.fs.cat(self._lm.get_abspath(s))
        except Exception, e:
            self.perror(e)

##############################################################################
# UI Firmware Functions
# firmware.*
#######################

    def complete_package_extract(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_cbf_unwrap(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_cbf_wrap_surgeon(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_cbf_wrap_kernel(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_cbf_summary(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_ubi_mount_erootfs(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_ubi_umount_erootfs(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_ubi_create_erootfs(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_jffs2_mount_erootfs(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_jffs2_umount_erootfs(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

    def complete_jffs2_create_erootfs(self, text, line, begidx, endidx):
        return self._lm.complete_local(text, line, begidx, endidx)

#######################
# UI Package Functions
# firmware.packages
#######################

    def do_package_extract(self, s):
        """
Usage:
    package_extract [path]

Extracts LF Package files (lfp ,lfp2)
Takes a file path, or will extract all packages in a directory.
Will overwrite without warning.
        """
        try:
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            packages.extract(abspath)
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_package_download(self, s):
        """
Usage:
    get_firmware <Didj|Explorer\LeapPad> <firmware|surgeon|bootloader>

Downloads the LF firmware package for device specified to files/<device>
Bootloader is for Didj only. Didj also has no surgeon.
Short names work also.
        """
        try:
            dtype, ftype = shlex.split(s)            
            lfp = packages.lf_packages()
            lfp.get_package(dtype, ftype)
        except Exception, e:
            self.perror(e)

#######################
# UI CBF File Functions
# firmware.cbf
#######################

    def do_cbf_unwrap(self, s):
        """
Usage:
    cbf_unwrap <file path>

Removes the CBF wrapper and prints a summary.
CBF is used on kernels and surgeon, to wrap a zImage or Image file.
Saves the image file to the same directory the cbf file was in.
If image file already exists will fail.
        """
        try:
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            cbf.extract(abspath)
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_cbf_wrap_surgeon(self, s):
        """
Usage:
    cbf_wrap_surgeon <file path>

Creates the CBF wrapper named surgeon.cbf and prints a summary.
CBF is used on kernels and surgeon, to wrap a zImage or Image file.
Saves the image file to the same directory the kernel file was in.
Kernel should be a zImage or Image file.
If cbf file already exists will fail.
        """
        try:
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            cbf.create(abspath, 'surgeon')
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_cbf_wrap_kernel(self, s):
        """
Usage:
    cbf_wrap_kernel <file path>

Creates the CBF wrapper named kernel.cbf and prints a summary.
CBF is used on kernels and surgeon, to wrap a zImage or Image file.
Saves the image file to the same directory the kernel file was in.
Kernel should be a zImage or Image file.
If cbf file already exists will fail.
        """
        try:
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            cbf.create(abspath, 'kernel')
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)



    def do_cbf_summary(self, s):
        """
Usage:
    cbf_summary <file path>

Display the CBF wrapper summary.
CBF is used on kernels and surgeon, to wrap a zImage or Image file.
        """
        try:
            self._lm.set_local()
            abspath = self._lm.get_abspath(s)
            cbf.summary(abspath)
            self._lm.last_location()
        except Exception, e:
            self._lm.last_location()
            self.perror(e)

#######################
# UI Firmware Images Functions
# firmware.images
#######################

    def do_ubi_mount_erootfs(self, s):
        """
Usage:
    ubi_mount <erootfs.ubi>

Mounts an Explorer erootfs.ubi image to /mnt/ubi_leapfrog
Caution this mounts an erootfs.ubi image specifically for the Explorer.
This is a Linux only command.
Will be prompted for password, sudo required for commands.
        """
        try:
            if sys.platform != 'win32':
                abspath = self._lm.get_abspath(s)
                u = ubi()
                u.mount(abspath)
            else:
                self.error('Linux only command.')
        except Exception, e:
            self.perror(e)



    def do_ubi_umount_erootfs(self, s):
        """
Usage:
    ubi_umount

Unmounts /mnt/ubi_leapfrog
This is a Linux only command.
Will be prompted for password, sudo required for commands.
        """
        try:
            if sys.platform != 'win32':
                u = ubi()
                u.umount()
            else:
                self.error('Linux only command.')
        except Exception, e:
            self.perror(e)



    def do_ubi_create_erootfs(self, s):
        """
Usage:
    ubi_create_erootfs path/to/rootfs/

Creates an Explorer erootfs.ubi image in the current directory.
Caution this image is specifically for the Explorer erootfs.
This is a Linux only command.
Will be prompted for password, sudo required for commands.
        """
        try:
            if sys.platform != 'win32':
                abspath = self._lm.get_abspath(s)
                u = ubi()
                u.create(abspath, self._lm.local_path)
            else:
                self.error('Linux only command.')
        except Exception, e:
            self.perror(e)



    def do_jffs2_mount_erootfs(self, s):
        """
Usage:
    jffs2_mount_erootfs <file_name>.jffs2

Mounts a Didj erootfs.jffs2 image to /mnt/jffs2_leapfrog
This is a Linux only command.
Will be prompted for password, sudo required for commands.
        """
        try:
            if sys.platform != 'win32':
                abspath = self._lm.get_abspath(s)
                j = jffs2()
                j.mount(abspath)
            else:
                self.error('Linux only command.')
        except Exception, e:
            self.perror(e)



    def do_jffs2_umount_erootfs(self, s):
        """
Usage:
    jffs2_umount_erootfs

Unmounts /mnt/jffs2_leapfrog
This is a Linux only command.
Will be prompted for password, sudo required for commands.
        """
        try:
            if sys.platform != 'win32':
                j = jffs2()
                j.umount()
            else:
                self.error('Linux only command.')
        except Exception, e:
            self.perror(e)



    def do_jffs2_create_erootfs(self, s):
        """
Usage:
    jffs2_create_erootfs path/to/rootfs/

Creates a Didj erootfs.jffs2 image in the current directory.
Caution this image is specifically for the Didj erootfs
This is a Linux only command.
Will be prompted for password, sudo required for commands.
        """
        try:
            if sys.platform != 'win32':
                abspath = self._lm.get_abspath(s)
                j = jffs2()
                j.create(abspath, self._lm.local_path)
            else:
                self.error('Linux only command.')
        except Exception, e:
            self.perror(e)
         
if __name__ == '__main__':
    OpenLFConnect().cmdloop()
        
