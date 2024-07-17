
from __future__ import print_function

from xaal.lib import Device,Engine,tools,bindings
import logging
import platform
from . import HTU21D
import logging

PACKAGE_NAME = "xaal.htu21d"

logger = logging.getLogger(PACKAGE_NAME)

def build_dev(addr,dev_type):
    dev            = Device(dev_type)
    dev.address    = addr
    dev.vendor_id  = "IHSEV"
    dev.version    = 0.1
    dev.info       = "%s@%s" % (PACKAGE_NAME,platform.node())
    dev.url        = "https://learn.adafruit.com/adafruit-htu21d-f-temperature-humidity-sensor/overview"
    dev.product_id = "HTU21D/I2C"
    return dev
        

def smooth(attribute,value,gap):
    old = attribute.value
    if not old:
        attribute.value = value
        return
    
    if not (old - gap <= value <= old + gap):
        attribute.value = value


class GW:
    def __init__(self,engine):
        self.engine = engine
        self.config()
        self.setup()
        
    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            logger.info('Missing config file, building a new one')
            cfg = tools.new_cfg(PACKAGE_NAME)
            cfg['config']['refresh'] = 1
            cfg['config']['thermometer'] = str(tools.get_random_uuid())
            cfg['config']['hygrometer'] = str(tools.get_random_uuid())
            cfg.write()
        self.cfg = cfg
        
    def setup(self):
        cfg = self.cfg['config']
        rate = float(cfg['refresh'])
        self.engine.add_timer(self.process,rate)

        thermometer_addr = tools.get_uuid(cfg['thermometer'])
        hygrometer_addr = tools.get_uuid(cfg['hygrometer'])

        # Just kidding w/ UUID 
        grp_uuid = bindings.UUID(bytes=thermometer_addr.bytes[:-2] + bytes(2)) + 0xeeff

        dev = build_dev(thermometer_addr,"thermometer.basic")
        dev.group_id = grp_uuid     
        self.temp = dev.new_attribute("temperature")
        self.engine.add_device(dev)
        
        dev = build_dev(hygrometer_addr,"hygrometer.basic")
        dev.group_id = grp_uuid
        self.hum = dev.new_attribute("humidity")
        self.engine.add_device(dev)

        self.sensor = HTU21D.HTU21D()
        
    def process(self):
        smooth(self.temp,round(self.sensor.read_temperature(),1),0.1)
        smooth(self.hum,round(self.sensor.read_humidity(),0),1)
    
def setup(eng):
    gw = GW(eng)
    return True
