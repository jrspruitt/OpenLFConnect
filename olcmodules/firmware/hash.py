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
# firmware.hash.py Version 0.1

from hashlib import md5, sha1


def error(e):
    assert False, '%s' % e



def get_md5(path):
    try:
        f = open(path, 'rb')
        md5h = md5()
        md5h.update(f.read())
        f.close()
        return md5h.hexdigest()
    except Exception, e:
        error(e)



def get_sha1(path):
    try:
        f = open(path, 'rb')
        sha1h = sha1()
        sha1h.update(f.read())
        f.close()
        return sha1h.hexdigest()
    except Exception, e:
        error(e)

