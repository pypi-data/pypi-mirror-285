from gevent import monkey; monkey.patch_all(thread=False)
import gevent

from xaal.lib import tools,Engine,Device
from xaal.schemas import devices

import platform
import logging
import serial
import time

PACKAGE_NAME = "xaal.edisio"
logger = logging.getLogger(PACKAGE_NAME)


def addr_to_str(addr):
    r = ""
    for k in addr:
        r = r + '%02x' % k
    return r


class GW(gevent.Greenlet):
    def __init__(self,engine):
        gevent.Greenlet.__init__(self)
        self.engine = engine
        self.config()
        self.setup()
        self.setup_gw()
        self.devices = {}

    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg = tools.new_cfg(PACKAGE_NAME)
            cfg['config']['port'] = '/dev/ttyUSB0'
            cfg['config']['base_addr'] = str(tools.get_random_base_uuid())
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg


    def setup(self):
        port = self.cfg['config'].get('port',None)
        if not port:
            logger.error('Please set Edisio serial port')
            return
        self.ser = serial.Serial(port,9600,timeout=0.1)

    def setup_gw(self):
        # last step build the GW device
        tmp = self.cfg['config'].get('addr',None)
        addr = tools.get_uuid(tmp)
        gw = devices.gateway(addr)
        gw.vendor_id  = "IHSEV"
        gw.product_id = "Edisio Gateway"
        gw.version    = 0.1
        gw.info       = "%s@%s" % (PACKAGE_NAME,platform.node())
        gw.attributes['embedded'] = []
        self.gw = gw
        self.engine.add_device(self.gw)

    def _run(self):
        self.stack = bytearray()
        self.last_pkt = bytearray()
        self.last_pkt_t = 0
        while 1:
            data = self.ser.read(16)
            if data:
                self.parse_data(data)

    def split(self,data):
        data_size = len(data)
        chunk = []
        result = data
        for i in range(0,data_size):
            if (i+4) > data_size:
                break
            if (data[i+1]==0x64) and (data[i+2]==0xd) and (data[i+3]==0xa):
                chunk=data[0:i]
                result = data[i+4:]
                break
        return chunk,result

    def parse_data(self,data):
        data = self.stack + data
        pkt,stack = self.split(data)
        if pkt:
            self.parse_pkt(pkt)
        self.stack = stack

    def filter(self,pkt):
        r = True
        if (pkt == self.last_pkt) and (time.time()-self.last_pkt_t < 0.5):
            r = False
        self.last_pkt = pkt
        self.last_pkt_t = time.time()
        return r

    def parse_pkt(self,pkt):
        if len(pkt)!=12:
            return
        if (pkt[0]==0x6c) and (pkt[1]==0x76) and (pkt[2]==0x63):
            if self.filter(pkt):
                addr = addr_to_str(pkt[3:7])
                btn = int(pkt[7])
                logger.debug("%s %s" % (addr, btn))
                self.send_notif(addr, btn)

    def send_notif(self, addr, btn):
        if addr not in self.devices.keys():
            self.add_buttons(addr)
        dev = self.devices[addr][btn-1]
        if dev:
            dev.send_notification('click')

    def add_buttons(self, addr):
        base_addr = tools.get_uuid(self.cfg['config'].get('base_addr'))
        group_id = base_addr + (int(addr, 16) << 8) + 0xff
        l = []
        addr_list = []
        for i in range(0, 8):
            tmp = base_addr + (int(addr, 16) << 8) + (i + 1)
            btn = Device('button.basic',tmp)
            btn.vendor_id = 'Edisio'
            btn.product_id = 'Edision Switches'
            btn.hw_id = 'Btn:%s/%s' % (addr, i)
            btn.info = 'Edisio ' + btn.hw_id
            btn.group_id = group_id
            l.append(btn)
            addr_list.append(btn.address)
            self.engine.add_device(btn)
        self.devices.update({addr: l})
        self.gw.attributes['embedded'] = self.gw.attributes['embedded'] + addr_list


def setup(engine):
    GW.spawn(engine)
    return True
