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
# initramfs.py Version 0.1
import os
from shutil import rmtree

import olcmodules.firmware.cbf as cbf


def error(e):
    assert False, e


def extract(path, suffix):
    if cbf.check(path, True):
        cbf.extract(path)
        path = os.path.join(os.path.dirname(path), 'zImage')

    irfs = initramfs(suffix)
    if irfs.gzip_find(irfs.file_open(path), True):
        irfs.extract(path)
        print 'Initramfs extracted.'
    else:
        error('Does not appear to be proper zImage.')
 

class initramfs():
    def __init__(self, suffix):
        self._GUNZIP_SIG = '\x1F\x8B\x08\x00'
        self._kernel_t = '/tmp/initramfs_t'
        self._cpio_t = '/tmp/initramfs.cpio'
        self._gzip_t = '/tmp/gzip_t.gz'
        self._cpio_cmd = 'sudo cpio --quiet -i --make-directories --preserve-modification-time --no-absolute-filenames -F %s' % self._cpio_t
        self._gzip_cmd = 'gunzip -cf %s' % self._gzip_t
        self._rootfs = 'rootfs.%s' % suffix
        self._rootfs_path = ''


    def error(self, e):
        assert False, e


    def extract(self, fname):
        self._rootfs_path = os.path.join(os.path.dirname(fname), self._rootfs)
        self.gzip_filter(fname)          
        self.cpio_extract()


    def file_write(self, buf, fname):
        try:
            f = open(fname, 'wb')
            f.write(buf)
            f.close()
            return True
        except Exception, e:
            self.prerror(e)


    def file_open(self, fname):
        try:
            f = open(fname, 'rb')
            buf =f.read()
            f.close()
            return buf
        except Exception, e:
            self.error(e)


    def gzip_filter(self, fname):
        buf = self.file_open(fname)
        self.gzip_find(buf)
        self.gzip_extract()


    def gzip_find(self, buf, test_file=False):
        check_gzip = self._GUNZIP_SIG in buf
        if test_file:
            return check_gzip
        else:
            if check_gzip:          
                idx = buf.index(self._GUNZIP_SIG)
                self.file_write(buf[idx:], self._gzip_t)
            else:
                self.error('gzip archive not found')


    def gzip_extract(self):
        try:
            p = os.popen(self._gzip_cmd, 'rb')
            buf = ''
            while 1:
                line = p.readline()
                buf += line
                if not line: break
            p.close()
            self.file_write(buf, self._kernel_t)
            print 'gzip extracted kernel image'
        except Exception, e:
            self.error(e)


    def cpio_extract(self):
        try:
            if os.path.exists(self._rootfs_path):
                rmtree(self._rootfs_path)          
            os.mkdir(self._rootfs_path)
            os.system('cd ' + self._rootfs_path + ';' + self._cpio_cmd)
        except Exception, e:
            self.error(e)