from xaal.schemas import devices
from xaal.lib import tools
import time
import logging
import functools
import gevent
from decorator import decorator

from . import tuyaclient

logger = logging.getLogger(__name__)


def get_dps(dps,idx):
    return dps.get(str(idx),None)

def now():
    return time.time()

class TuyaDev:
    def __init__(self,tuya_id,cfg,parent):
        self.is_valid = False
        self.tuya_id = tuya_id
        self.parent = parent
        self.devices = []
        self.last_update = 0
        self.debug = False
        self.cfg = cfg
        self.load_config()
        self.setup()
        self.init_properties()
        self.tuya_client.subscribe(self.event_handle)

    @property
    def connected(self):
        return self.tuya_client.connected

    def load_config(self):
        cfg = self.cfg
        addr  = tools.get_uuid(cfg.get('base_addr',None))
        ip    = cfg.get('ip',None)
        key   = cfg.get('key',None)
        proto = cfg.get('protocol','3.3')
        self.debug = cfg.get('debug', False)
        # invalid file ?
        if not ip or not key: return

        if addr == None:
            addr = tools.get_random_base_uuid()
            cfg['base_addr'] = str(addr)
        self.base_addr = addr

        # forge the dict needed for tuyaface
        device = { 'ip' : ip, 'deviceid' : self.tuya_id, 'localkey' : key,'protocol' : proto }
        self.tuya_client = tuyaclient.TuyaClient(device)
        self.tuya_client.start()
        self.is_valid = True

    def init_properties(self):
        for dev in self.devices:
            dev.vendor_id = 'IHSEV / Tuya'
            dev.hw_id = self.tuya_id
            dev.info = 'Tuya %s: @ %s' % (self.__class__.__name__,self.tuya_client.ip)
            if len(self.devices) > 1:
                dev.group_id = self.base_addr + 0xff

    def event_handle(self,ev_type,ev_data):
        if ev_type == tuyaclient.Event.DPS:
            if self.debug:
                logger.debug(f"RECV {self.tuya_id} DPS: {ev_data}")
            self.on_dps(ev_data)

        elif ev_type == tuyaclient.Event.CONNECTED:
            self.request_dps()
            self.parent.update_inactive()

        elif ev_type == tuyaclient.Event.DISCONNECTED:
            self.parent.trigger_update_inactive()

    def post_dps(self,data):
        if self.debug:
            logger.debug(f"POST {self.tuya_id} DPS: {data}")
        self.tuya_client.post_dps(data)

    def request_dps(self):
        if self.debug:
            logger.debug(f"REQUEST {self.tuya_id}")
        self.tuya_client.request_dps()

    def setup(self):
        logger.warning('Please override setup()')

    def on_dps(self,data):
        logger.warning('Please implement on_status in your class')


class PowerRelay(TuyaDev):
    def setup(self):
        dps  = self.cfg.get('dps',['1'])
        addr = self.base_addr+1
        self.dps_to_dev = {}
        for k in dps:
            dev = devices.powerrelay_toggle(addr)
            dev.methods['turn_on'] = functools.partial(self.turn_on,k,dev)
            dev.methods['turn_off'] = functools.partial(self.turn_off,k,dev)
            dev.methods['toggle'] = functools.partial(self.toggle,k,dev)
            self.dps_to_dev.update({k:dev})
            self.devices.append(dev)
            addr = addr +1

    def turn_on(self,idx,dev):
        self.post_dps({idx:True})

    def turn_off(self,idx,dev):
        self.post_dps({idx:False})

    def toggle(self,idx,dev):
        self.post_dps({idx:not dev.attributes[0].value})

    def on_dps(self,dps):
        for k in dps:
            tmp = self.dps_to_dev.get(k,None)
            if tmp:
                tmp.attributes['power'] = dps[k]


def out_hysteresis(value,new_value,tol):
    if value == None:
        return True
    mini = value - tol
    maxi = value + tol
    if mini < new_value < maxi:
        return False
    return True


class SmartPlug(PowerRelay):

    def setup(self):
        self.pmeter_dps = self.cfg.get('pmeter_dps',['4','5','6'])
        pmeter = devices.powermeter(self.base_addr)
        pmeter.new_attribute('voltage')
        pmeter.new_attribute('current')
        pmeter.del_attribute(pmeter.get_attribute('energy'))
        pmeter.unsupported_attributes = ['energy']
        self.devices.append(pmeter)
        PowerRelay.setup(self)
        # related power relays
        pmeter.attributes['devices'] = [k.address for k in self.devices[1:]]

    def debug_dps(self, dps):
        k_dps = list(self.dps_to_dev.keys())
        k_dps = k_dps + self.pmeter_dps
        r = ''
        for k,v in dps.items():
            if k not in k_dps:
                r = r + f"'{k}'->{v}    "
        if len(r) > 0:
            logger.info(f"{self.tuya_id} unknow DPS: {r}")

    def on_dps(self,dps):
        if self.debug:
            self.debug_dps(dps)
        PowerRelay.on_dps(self,dps)
        pmeter_attr = self.devices[0].attributes
        # current 
        current = get_dps(dps,self.pmeter_dps[0])
        if current!=None:
            tmp = round(int(current) / 1000,2)
            if out_hysteresis(pmeter_attr['current'],tmp,0.02):
                pmeter_attr['current'] = tmp
        # power 
        power = get_dps(dps,self.pmeter_dps[1])
        if power!=None:
            tmp = round(int(power) / 10)
            if out_hysteresis(pmeter_attr['power'],tmp,2):
                pmeter_attr['power'] = tmp
        # voltage
        voltage = get_dps(dps,self.pmeter_dps[2])
        if voltage!=None:
            tmp = round(int(voltage) / 10)
            if out_hysteresis(pmeter_attr['voltage'],tmp,2):
                pmeter_attr['voltage'] = tmp



class Lamp(TuyaDev):
    def setup(self):
        dev = devices.lamp_toggle(self.base_addr+1)
        dev.methods['turn_on'] = self.turn_on
        dev.methods['turn_off'] = self.turn_off
        dev.methods['toggle'] = self.toggle
        self.devices.append(dev)

    def turn_on(self):
        self.post_dps({1:True})

    def turn_off(self):
        self.post_dps({1:False})

    def toggle(self):
        self.post_dps({1:not self.devices[0].attributes['light']})

    def on_dps(self,dps):
        state = get_dps(dps,1)
        if state != None:
            self.devices[0].attributes['light'] = state

class AdvLampMixin:
    """ 
    Dimming Lamp & RGB Lamp shares the config & API, but the dps (in & out) are 
    really differents
    """

    def setup_mixin(self,dev):
        dev.methods['turn_on'] = self.turn_on
        dev.methods['turn_off'] = self.turn_off
        dev.methods['set_white_temperature'] = self.set_white_temperature
        dev.methods['set_brightness'] = self.set_brightness
        dev.methods['toggle'] = self.toggle
        self.devices.append(dev)

        # setting up white balance min/max
        white_temp=self.cfg.get('white_temp',None)
        if white_temp:
            self.white_min = int(white_temp[0])
            self.white_max = int(white_temp[1])
        else:
            self.white_min = 1500
            self.white_max = 6500

    def brightness_to_dps(self,value):
        try:
            res = round(int(value) * 255 / 100)
        except ValueError:return
        if res < 25: res = 25
        if res > 255: res = 255
        return res

    def temperature_to_dps(self,value):
        try:
            res = int(value)
        except ValueError:return
        delta = (self.white_max - self.white_min) / 255.0
        target = int((res - self.white_min) / delta)
        if target > 255: target = 255
        if target < 0: target = 0 
        return target



class LampDimmer(Lamp,AdvLampMixin):
    def setup(self):
        dev = devices.lamp_dimmer(self.base_addr+1)
        self.setup_mixin(dev)

    def on_dps(self,dps):
        attrs = self.devices[0].attributes
        # state
        result = get_dps(dps,1)
        if result!=None:
            attrs['light'] = result
        # brightness
        result = get_dps(dps,2)
        if result:
            value = int(result) * 100 / 255
            attrs['brightness'] = int(value)
        # white_temperature
        result = get_dps(dps,3)
        if result:
            delta = (self.white_max - self.white_min) / 255.0
            value = int(result) * delta +  self.white_min
            attrs['white_temperature'] = round(value)

    def set_white_temperature(self,_white_temperature):
        tmp = self.temperature_to_dps(_white_temperature)
        self.post_dps({3:tmp})

    def set_brightness(self,_brightness,_smooth=0):
        # smooth is not supported
        tmp = self.brightness_to_dps(_brightness)
        self.post_dps({2:tmp})


class LampRGB(Lamp,AdvLampMixin):
    SCENES = ['scene_1','scene_2','scene_3','scene_4']

    def setup(self):
        dev = devices.lamp_color(self.base_addr+1)
        dev.methods['set_hsv'] = self.set_hsv
        dev.methods['set_mode'] = self.set_mode
        dev.methods['get_scenes'] = self.get_scenes
        dev.methods['set_scene'] =  self.set_scene
        self.setup_mixin(dev)

    def on_dps(self,dps):
        attrs = self.devices[0].attributes
        # state
        result = get_dps(dps,1)
        if result!=None:
            attrs['light'] = result
        # color / white 
        result = get_dps(dps,2)
        if result == 'colour': attrs['mode'] = 'color'
        if result == 'white':  attrs['mode'] = 'white'
        if result and result.startswith('scene'): attrs['mode'] = 'scene'
        # brightness
        result = get_dps(dps,3)
        if result:
            value = int(result) * 100 / 255
            attrs['brightness'] = int(value)
        # white_temperature
        result = get_dps(dps,4)
        if result:
            delta = (self.white_max - self.white_min) / 255.0
            value = int(result) * delta +  self.white_min
            attrs['white_temperature'] = round(value)
        # color value (hsv)
        result = get_dps(dps,5)
        if result:
            attrs['hsv'] = tuyaclient.hexvalue_to_hsv(result)

    def set_white_temperature(self,_white_temperature):
        tmp = self.temperature_to_dps(_white_temperature)
        self.post_dps({2:'white',4:tmp})

    def set_brightness(self,_brightness,_smooth=0):
        # smooth is not supported
        tmp = self.brightness_to_dps(_brightness)
        self.post_dps({2:'white',3:tmp})

    def set_hsv(self,_hsv,_smooth=0):
        hsv = [float(k) for k in list(_hsv.split(','))]
        result = tuyaclient.color_to_hex(hsv)
        self.post_dps({2:'colour',5:result})

    def set_mode(self,_mode):
        if _mode == 'color':
            self.post_dps({2:'colour'})
        if _mode == 'white':
            self.post_dps({2:'white'})
        if _mode == 'scene':
            self.post_dps({2:'scene_4'})
        
    def get_scenes(self):
        return LampRGB.SCENES

    def set_scene(self,_scene):
        if _scene in LampRGB.SCENES:
            self.post_dps({2:_scene})
