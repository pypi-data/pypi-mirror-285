#!/usr/bin/env python

from xaal.lib import Engine,helpers,tools,cbor
from xaal.monitor import monitor
from xaal.schemas import devices

import threading
import logging
import time

import os, stat, errno
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse
import json

if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, probably it's too old.")

PACKAGE = 'xaal.fuse'

fuse.fuse_python_api = (0, 2)
logger = logging.getLogger()
helpers.setup_console_logger()

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 4096
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class XAALFS(Fuse):

    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        self.mon = None
        xaal = threading.Thread(target=self.xaal_thread,daemon=True)
        xaal.start()

    def xaal_thread(self):
        cfg = tools.load_cfg(PACKAGE)
        if not cfg:
            cfg = tools.new_cfg(PACKAGE)
            cfg.write()
        addr = tools.get_uuid(cfg['config'].get('addr'))
        db_server = tools.get_uuid(cfg['config'].get('db_server'))
        if not db_server:
            logger.warning('Please set db_server in config file')
        eng = Engine()
        dev = devices.hmi(addr)
        dev.info = PACKAGE
        eng.add_device(dev)
        self.mon = monitor.Monitor(dev,db_server=db_server)
        eng.run()

    def getattr(self, path):
        #print("getattr %s" % path)
        data = path.split('/')
        dev = None

        st = MyStat()
        st.st_nlink = 2
        if path =='/':
            st.st_mode = stat.S_IFDIR | 0o755
            return st

        if len(data) > 1:
            target = tools.get_uuid(data[1])
            dev = self.devices.get_with_addr(target)

        if (len(data) == 2 and dev):
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_mtime = dev.last_alive
            return st

        if (len(data) == 3 and dev and data[2] in ['attributes','description','db']):
            if data[2] == 'attributes': 
                #st.st_size = len(dev.attributes)
                st.st_mtime = dev.attributes.last_update
            if data[2] == 'description': 
                #st.st_size = len(dev.description)
                st.st_mtime = dev.description.last_update
            if data[2] == 'db':
                #st.st_size = len(dev.db)
                st.st_mtime = dev.db.last_update
            
            st.st_mode = stat.S_IFREG | 0o444
            st.st_nlink = 1
            return st

        return -errno.ENOENT

    @property
    def devices(self):
        if hasattr(self.mon,'devices'):
            return self.mon.devices
        return monitor.Devices()

    def dir_entries(self,values):
        for r in  ['.', '..'] + values :
            yield fuse.Direntry(r)

    def readdir(self, path, offset):
        data = path.split('/')
        if path=='/':
            return self.dir_entries([k.address.str for k in self.devices])
        if len(data) == 2:
            target = tools.get_uuid(data[1])
            dev = self.devices.get_with_addr(target)
            if dev:
                return self.dir_entries(['attributes','db','description'])
        return self.dir_entries([])
        

    def open(self, path, flags):
        data = path.split('/')
        if (len(data)==3 and data[-1] in ['attributes','db','description']) : 
            accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
            if (flags & accmode) != os.O_RDONLY:
                return -errno.EACCES
        else:
            return -errno.ENOENT

    def read(self,path,size,offset):
        data = path.split('/')
        dev = None 
        if len(data) > 1:
            target = tools.get_uuid(data[1])
            dev = self.devices.get_with_addr(target)
        if len(data) == 3 and dev and data[-1] in ['attributes','db','description']:
            tmp = None
            if data[2] == 'attributes': tmp = dev.attributes
            if data[2] == 'db': tmp = dev.db
            if data[2] == 'description': tmp = dev.description
            if tmp:
                cbor.cleanup(tmp)
                return json.dumps(tmp,indent=2).encode('utf-8')
        return b''

def main():
    usage=""" xAAL Fuse filesystem \n""" + Fuse.fusage
    import sys
    if sys.argv[-1] != '-f':
        print(usage)
        print("Please run this in foreground (-f)")
        return
    server = XAALFS(version="%prog " + fuse.__version__,usage=usage,dash_s_do='setsingle')
    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
