from gevent import monkey; monkey.patch_all(thread=False)
import gevent

from xaal.lib import tools,Device
from . import devices

import platform
import socket
import time
import logging

PACKAGE_NAME = "xaal.ipx800"
logger = logging.getLogger(PACKAGE_NAME)

class GW(gevent.Greenlet):
    def __init__(self,engine):
        gevent.Greenlet.__init__(self)
        self.engine = engine
        self.cfg = tools.load_cfg_or_die(PACKAGE_NAME)
        self.connect()
        self.setup_ouputs()
        self.setup_gw()
        
    def connect(self):
        """ create the ipx sock"""
        cfg = self.cfg['config']
        host = cfg['host']
        port = int(cfg['port'])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        logger.info("IPX800 connected")
        
    def setup_ouputs(self):
        """ load nodes from config file"""
        cfg = self.cfg['outputs']
        self.in_out=[]

        i = 0
        group = cfg['group']
        base_addr = tools.get_uuid(cfg['base_addr']) 
        for t in cfg['outputs_type']:
            i = i+1
            out = None
            addr = base_addr + i

            if t == 'relay':
                out = devices.new_relay(self,i,addr,group)
            if t == 'lamp':
                out = devices.new_lamp(self,i,addr,group)
            if out:
                self.engine.add_device(out.dev)
                self.in_out.append(out)

    def setup_gw(self):
        # last step build the GW device
        gw            = Device("gateway.basic")
        gw.address    = tools.get_uuid(self.cfg['config']['addr']) 
        gw.vendor_id  = "IHSEV"
        gw.product_id = "IPX-800 Ethernet Control System"
        gw.version    = 0.1
        gw.url        = "http://gce-electronics.com/fr/home/57-module-ip-rail-din-webserver-8-relais-ipx800-v3.html"
        gw.info       = "%s@%s" % (PACKAGE_NAME,platform.node())

        emb = gw.new_attribute('embedded',[])
        emb.value = [io.dev.address for io in self.in_out]
        self.engine.add_device(gw)
        self.send('GetOutputs')

    def _run(self):
        while 1:
            try:
                line = self.sock.makefile().readline().strip('\r\n')
            except Exception as e:
                self.network_error(e)
            else:
                self.parse_line(line)
        
    def parse_line(self,line):
        #logger.debug(line)
        if line == 'OK': return

        if line.startswith('I='):
            data = line.split('&')
            if len(data) == 26:
                out = data[1][2:]
                self.parse_output(out)
        elif len(line)==32:
            self.parse_output(line)

    def parse_output(self,data):
        i = 0
        for c in data:
            i = i + 1 
            for io in self.in_out:
                if io.chan == i:
                    io.state.value = bool(int(c))
                    break
        
    def send(self,data):
        logger.debug(data)
        data = data  + "\r\n"
        self.sock.send(data.encode('utf-8'))
        time.sleep(0.07)

    def network_error(self,msg):
        logger.warning("Network Error IPX800: %s" %msg)
        self.sock.close()
        self.connect()
        time.sleep(2)
        
    def relay_on(self,ID):
        msg = 'Set%02d1' % ID
        self.send(msg)

    def relay_off(self,ID):
        msg = 'Set%02d0' % ID
        self.send(msg)


def setup(engine):
    GW.spawn(engine)
    return True
