#!/bin/usr/env python

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