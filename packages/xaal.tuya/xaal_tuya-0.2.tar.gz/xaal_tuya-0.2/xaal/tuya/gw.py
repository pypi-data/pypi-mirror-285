from gevent import monkey;monkey.patch_all(thread=False)


from xaal.lib import tools,Device
from xaal import schemas
from . import devices

import atexit
import logging
import time

PACKAGE_NAME = 'xaal.tuya'
logger = logging.getLogger(__name__)

CFG_MAP = { 'power_relay'  : devices.PowerRelay,
            'smart_plug'   : devices.SmartPlug ,
            'lamp'        : devices.Lamp,
            'lamp_dimmer' : devices.LampDimmer,
            'lamp_rgb'   : devices.LampRGB, }

class GW:
    def __init__(self,engine):
        self.booted = False
        self.engine = engine
        self.devices = {}
        atexit.register(self._exit)
        self.config()
        self.setup()
        engine.add_timer(self.boot,10,1)
        engine.add_timer(self.update,4*60)
        
    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['devices'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg

    def setup(self):
        addr = tools.get_uuid(self.cfg['config']['addr'])
        gw = schemas.devices.gateway(addr)
        gw.vendor_id  = 'IHSEV'
        gw.product_id = 'Generic Tuya Gateway'
        gw.info       = 'Tuya Gateway'
        gw.attributes['embedded'] = []
        gw.attributes['inactive'] = []
        self.gw = gw

        devs = self.cfg.get('devices',[])
        for d in devs:
            cfg = devs.get(d,{})
            tmp = cfg.get('type','PowerRelay')
            dev_type = CFG_MAP.get(tmp,None)
            if dev_type:
                dev = dev_type(d,cfg,self)
                if dev.is_valid:
                    self.add_device(d,dev)
                else:
                    logger.warning(f"Config error for {d}")
            else:
                logger.warn(f"Unsupported device type {tmp} {d}")

        # loaded all devices
        self.engine.add_device(gw)

    def add_device(self,tuya_id,dev):
        self.devices[tuya_id] = dev
        for d in dev.devices:
            self.engine.add_device(d)
            self.gw.attributes['embedded'].append(d.address)

    def trigger_update_inactive(self):
        self.gw.engine.add_timer(self.update_inactive,5,1)

    def boot(self):
        logger.info('Booted')
        self.booted = True
        self.update_inactive()

    def update_inactive(self):
        if self.booted == False:
            return

        r = []
        for dev in self.devices.values():
            if not dev.connected:
                r = r + [k.address for k in dev.devices]
        if set(self.gw.attributes['inactive']) != set(r):
            self.gw.attributes['inactive'] = r

    def update(self):
        now = time.time()
        for dev in self.devices.values():
            dev.request_dps()
        
    def _exit(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()

def setup(eng):
    GW(eng)
    return True
