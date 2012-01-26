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
# services/interface.py Version 0.5
class config(object):
    def __init__(self, connection):
        self._connection = connection



    def get_root_dir(self):
        return self._connection.get_root_dir_i()
    
    root_dir = property(get_root_dir)



    def get_device_id(self):
        try:
            return self._connection.get_device_id_i()
        except Exception, e:
            self._connection.rerror(e)

    device_id = property(get_device_id)



    def get_host_id(self):
        try:
            return self._connection.get_host_id_i()
        except Exception, e:
            self._connection.rerror(e)
            
    host_id = property(get_host_id)


    def is_connected(self):
        try:
            return self._connection.is_connected_i()
        except Exception, e:
            self._connection.rerror(e)

if __name__ == '__main__':
    print 'No examples yet.'