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
# Version: Version 0.5
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
import os
import sys

from olcmodules.clients.local import client as local_client
from olcmodules.clients.interface import filesystem as fs_iface

class manager(object):
    def __init__(self, init_path, cmd=None):
        if cmd is not None:
            self._cmd = cmd
            self._prompt_suffix = '> '
            self._cmd.prompt = 'local%s' % self._prompt_suffix
        
        self.local_client = local_client(False)
        self.remote_client = None
        
        self.remote_conn = None
        self._remote_set = False
        self._last_location = self._remote_set
        
        self._local_fs = fs_iface(self.local_client)
        self._remote_fs = None        
        self.fs = self._local_fs
        
        self._local_path_init = init_path
        self.local_path = self._local_path_init
        self._remote_path_init = '/'
        self.remote_path = self._remote_path_init        
        self.path = ''


##############################################################################
# Internal Functions
# location
#######################

    def error(self, e):
        assert False, '%s' % e

#######################
# Internal Set Location Functions
# location
#######################

    def set_remote(self, path=''):
        if path:
            self.remote_path = path
        self.fs = self._remote_fs
        self.path = self.remote_path
        self._last_location = self._remote_set
        self._remote_set = True
        if self._cmd is not None:
            self._cmd.prompt = 'remote%s' % self._prompt_suffix



    def set_local(self, path=''):
        if path:
            self.local_path = path
        self.fs = self._local_fs
        self.path = self.local_path
        self._last_location = self._remote_set
        self._remote_set = False
        if self._cmd is not None:
            self._cmd.prompt = 'local%s' % self._prompt_suffix



    def last_location(self):
        if self._last_location:
            self._remote_set = self._last_location
            self.set_remote()
        else:
            self._remote_set = self._last_location
            self.set_local()

#######################
# Internal Remote Local Internal Client/Connection Functions
# location
#######################

    def is_client(self, client):
        connected = False
        
        if self.remote_client:
            connected = self.remote_conn.is_connected()

            if connected:
                              
                if client is self.remote_client:
                    return True
                elif client is not self.remote_client:
                    self.error('Another remote client is currently running.')

            else:
                self.remote_destroy()

        return False



    def is_remote(self, client=False):
        connected = False
        
        if self.remote_client:
            connected = self.remote_conn.is_connected()
            
            if not connected:
                self.remote_destroy()
                self.error('Device is not connected.')
            
        else:
            self.remote_destroy()
            self.error('No remote client is running.')
            
            
        if client is False:
            return True
        elif client is self.remote_client:
            return True
        else:
            self.error('Wrong command for the current remote client.')
        


    def remote_connection_init(self, conn_iface, fs_iface, client):
        self.remote_client = client
        self.remote_conn = conn_iface
        self._remote_fs = fs_iface



    def remote_path_init(self):
        if self.remote_conn:
            self.set_remote(self.remote_conn.root_dir)
        else:
            self.set_local()
            self.error('No remote module present.')
 
 
 
    def remote_destroy(self):
        self.remote_client = None
        self.remote_conn = None
        self._remote_fs = None
        self._remote_set = False
        self.remote_path = self._remote_path_init
        self.set_local(self._local_path_init)

#######################
# Internal Remote Local Path Formatting Functions
# location
#######################

    def is_empty(self, s):
        if s == '':
            self.error('No path was set.')
        else:
            return True



    def set_path(self, path):
        if self._remote_set:            
            if self.fs.is_dir(path):
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
            return '%s/' % os.path.splitdrive(self.local_path)[0]
        else:
            return '/'



    def get_abspath(self, stub):
        if stub.startswith(self.get_path_prefix()):
            path = stub
        else:
            path = os.path.join(self.path, stub)
        if sys.platform == 'win32' and self._remote_set:
            ret = os.path.normpath(path).replace('\\', '/')
        else:
            ret = os.path.normpath(path)

        return ret

#######################
# Internal Remote Local Path Completion Functions
# location
#######################

    def get_dir_list(self, path):
        try:
            dlist = self.fs.dir_list(path)
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

if __name__ == '__main__':
    print 'No examples yet.'