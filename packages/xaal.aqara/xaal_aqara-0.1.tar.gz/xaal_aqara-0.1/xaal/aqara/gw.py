from gevent import monkey; monkey.patch_all(thread=False)

from xaal.lib import tools
from .network import AqaraConnector,AqaraDiscovery
from . import devices

import atexit
import logging

PACKAGE_NAME = 'xaal.aqara'
logger = logging.getLogger(PACKAGE_NAME)


class GW(object):
    def __init__(self,engine):
        self.engine = engine
        self.devices = {}
        atexit.register(self._exit)
        self.config()
        self.setup()
        
    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['devices'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg

    def add_device(self,sid,model,base_addr):
        """ find the device class for model, and add it to the engine"""
        klass = devices.find_device_class(model)
        if klass:
            dev = klass(sid,model,base_addr,self)
            self.engine.add_devices(dev.devices)
            self.devices.update({sid:dev})
            return dev
        else:
            logger.info(f"Unsupported device {model} / {sid}")
            return None

    def setup(self):
        """Start Aqara mutlicast senders / receivers"""
        self.aqara = AqaraConnector.spawn(self)
        self.disco = AqaraDiscovery.spawn(self)
        # schedule a whois request every 2 min
        self.engine.add_timer(self.disco.whois,120,-1)
    
    def get_device(self,sid,model):
        cfg = self.cfg['devices']
        # Already running device ? 
        if sid in self.devices.keys():
            return self.devices[sid]
        # Already known device ? 
        elif sid in cfg:
            dev_cfg = cfg.get(sid)
            model_old = dev_cfg.get('model',None)
            base_addr = tools.get_uuid( dev_cfg.get('base_addr',None) ) 
            dev = None
            if base_addr == None:
                logger.warn(f"Device w/ bad base_addr {sid}")
            if model != model_old:
                logger.warn(f"Device {sid} wrong model")
            if model and base_addr:
                dev = self.add_device(sid,model,base_addr)
                if dev and model == 'gateway':
                    dev.secret = dev_cfg.get('secret',None)
            return dev
        # Still not found ? => new device
        else:
            base_addr = tools.get_random_base_uuid()
            dev = self.add_device(sid,model,base_addr)
            if dev:
                logger.warning(f"Discover new Aqara Device {model} {sid}")
                cfg = {'base_addr' : str(base_addr),'model':model}
                self.cfg['devices'].update({sid:cfg})
            return dev

    def on_receive(self,pkt):
        """ Message callback, check network"""
        sid = pkt.get('sid',None)
        if not sid: return
        model = pkt.get('model',None)
        dev = self.get_device(sid,model)
        if dev:
            dev.parse(pkt)

    def _exit(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()

def setup(eng):
    logger.info('Starting %s' % PACKAGE_NAME)
    #GW.spawn(eng)
    gw = GW(eng)
    return True
