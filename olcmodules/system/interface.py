#!/bin/usr/env python

class config(object):
    def __init__(self, link):
        self._link = link


    def get_conn_type(self):
        return self._link.get_conn_type_i()
    
    conn_type = property(get_conn_type)


    def get_root_dir(self):
        return self._link.get_root_dir_i()
    
    root_dir = property(get_root_dir)



    def get_device_id(self):
        try:
            return self._link.get_device_id_i()
        except Exception, e:
            self._link.rerror(e)

    def set_device_id(self, did):
        try:
            if self._link.device_check(id):
                self._link.set_device_id_i(did)
        except Exception, e:
            self._link.rerror(e)

    device_id = property(get_device_id, set_device_id)



    def get_host_id(self):
        try:
            return self._link.get_host_id_i()
        except Exception, e:
            self._link.rerror(e)

    def set_host_id(self, hid):
        try:
            if self._link.host_check(hid):
                self._link.set_host_id_i(hid)
        except Exception, e:
            self._link.rerror(e)
            
    host_id = property(get_host_id, set_host_id)


    def is_connected(self):
        try:
            return self._link.is_connected_i()
        except Exception, e:
            self._link.rerror(e)

if __name__ == '__main__':
    print 'No examples yet.'