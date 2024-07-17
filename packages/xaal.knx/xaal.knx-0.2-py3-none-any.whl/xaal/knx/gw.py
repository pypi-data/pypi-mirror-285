from gevent import monkey;monkey.patch_all(thread=False)
import gevent

from xaal.lib import tools,Device,Engine
from .knxrouter import KNXConnector,KNXcEMIException
from . import devices

import inspect
import atexit
import logging

PACKAGE_NAME = 'xaal.knx'
logger = logging.getLogger(PACKAGE_NAME)

def device_class_finder():
    """ look trought the devices module to find binding class"""
    BLACK_LIST = ['KNXDev','partial']
    result = {}
    dict_ = devices.__dict__
    for k in dir(devices):
        target = dict_[k]
        if (inspect.isclass(target)) and (k not in BLACK_LIST):
            if str(k).endswith('Mixin'):continue
            result.update({k.upper():target})
    return result

class GW(gevent.Greenlet):
    def __init__(self,engine):
        gevent.Greenlet.__init__(self)
        self.engine = engine
        self.devices = []
        self.save_config = False
        atexit.register(self._exit)
        self.config()
        self.setup()
        self.refresh()

    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['devices'] = []
            logger.warn("Created an empty config file, please add your devices")
            cfg.write()
        self.cfg = cfg

    def setup(self):
        addr = self.cfg['config'].get('phy_addr',None)
        if addr:
            self.knx = KNXConnector(addr)
        else:
            self.knx = KNXConnector()

        devs = self.cfg['devices']
        devices_class = device_class_finder()
        for k in devs:
            type_ = devs[k].get('type',None)
            klass = None
            if type_:            
                klass = devices_class.get(devs[k]['type'].upper(),None)
            if klass:
                dev = klass(self,devs[k])
                xaal_dev = dev.dev
                xaal_dev.vendor_id = 'IHSEV'
                xaal_dev.version = 0.1
                xaal_dev.product_id = 'KNX ' + type_
                self.devices.append(dev)
            else:
                logger.warn("Unkown device type %s %s" % (type_,k))

        l = [k.dev for k in self.devices]
        self.engine.add_devices(l)
        # schedule a refresh of KNX network. usefull for wifi network
        refresh_rate = self.cfg['config'].get('refresh_rate',None)
        if refresh_rate:
            self.engine.add_timer(self.refresh,int(refresh_rate))
        

    def _run(self):
        while 1:
            try:
                cemi = self.knx.receive()
            except KNXcEMIException as e:
                logger.warn("Wrong cemi frame: " +str(e))
                cemi = None
            if cemi:
                logger.debug("Receing: %s" % cemi)
                self.handle(cemi)

    def handle(self,cemi):
        for dev in self.devices:
            if cemi.group_addr in dev.attributes_binding :
                dev.parse(cemi)

    def refresh(self):
        """loop throught the device adress to find values"""
        for dev in self.devices:
            for ga in dev.attributes_binding:
                self.knx.read(ga)

    def _exit(self):
        # TODO : drop the save_config flag, reloading cfg is better
        if self.save_config:
            logger.info('Saving configuration file')
            self.cfg.write()

def setup(eng):
    GW.spawn(eng)
    return True
