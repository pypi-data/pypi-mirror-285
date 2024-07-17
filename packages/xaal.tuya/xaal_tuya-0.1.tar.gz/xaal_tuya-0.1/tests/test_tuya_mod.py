from gevent import monkey;monkey.patch_all()
import gevent

import tuyaface as tuya
import time
import colorsys

import coloredlogs
coloredlogs.install('DEBUG')


import logging
logger = logging.getLogger(__name__)

# lamp LSC
d1 = {  'ip' : '192.168.1.65', 'deviceid' : 'bf017829869d45e15dld7g','localkey' : 'efb36814ce74ee7d', 'protocol' : '3.3' }

# SHP6-test
d2 = {  'ip' : '192.168.1.63','deviceid' : '142200252462ab419539','localkey' : '6eeec6c9eeeff233','protocol' : '3.3'}

# alĥaplug-2
d3 = {  'ip' : '192.168.1.61','deviceid' : '74012545dc4f229f058f','localkey' : 'e3e182a7491f2d44','protocol' : '3.3'}

# shp-7
d4 = {  'ip' : '192.168.1.66', 'deviceid' : '42361312d8f15bd5a25d','localkey' : 'af6430180fd6dde7', 'protocol' : '3.3' }

# LSC edison
d5 = {  'ip' : '192.168.1.172', 'deviceid' : '40005734840d8e4d5500','localkey' : 'da6d966a4585ced5', 'protocol' : '3.3' }

# utorch rgb
d6 = {  'ip' : '192.168.1.162', 'deviceid' : '00747018f4cfa262ea13','localkey' : 'f598419fef804b7f', 'protocol' : '3.3' }



d0 = {  'ip' : '192.168.1.60', 'deviceid' : '42361312d8f15bd5a25d','localkey' : 'af6430180fd6dde7', 'protocol' : '3.3' }




devices = [d1,d2,d3,d4]

def color_to_hex(hsv):
    "hue is 0 to 360, sat & brighness between 0 to 1"

    # ensure we received a list 
    hsv = list(hsv)
    hsv[0] = hsv[0] / 360.0
    h,s,v = hsv
    rgb = [int(i*255) for i in colorsys.hsv_to_rgb(h,s,v)]

    # This code from the original pytuya lib
    hexvalue = ""
    for value in rgb:
        temp = str(hex(int(value))).replace("0x","")
        if len(temp) == 1:
            temp = "0" + temp
        hexvalue = hexvalue + temp

    hsvarray = [int(hsv[0] * 360), int(hsv[1] * 255), int(hsv[2] * 255)]
    hexvalue_hsv = ""
    for value in hsvarray:
        temp = str(hex(int(value))).replace("0x","")
        if len(temp) == 1:
            temp = "0" + temp
        hexvalue_hsv = hexvalue_hsv + temp
    if len(hexvalue_hsv) == 7:
        hexvalue = hexvalue + "0" + hexvalue_hsv
    else:
        hexvalue = hexvalue + "00" + hexvalue_hsv
    return hexvalue


def _toggle(dev,idx=1):
    status = tuya.status(dev)
    logger.info(status)
    time.sleep(0.1)
    state = get_dps(status,idx)
    return tuya.set_state(dev,not state,idx)


def run_cmd(cmd,*args,**kwargs):
    cnt = 1
    while 1:
        try:
            result = cmd(*args,**kwargs)
            if result:
                return result
        except ConnectionResetError:
            logger.error('ConnectionResetError: w/ %s (%s)' % (args,cnt))
        except OSError:
            logger.error('OSError: w/ %s (%s)' % (args,cnt))
        # error 
        if cnt == 2: break
        cnt = cnt+1
        time.sleep(0.3)

def get_dps(data,idx):
    if data:
        dps = data.get('dps',{})
        return dps.get(str(idx),None)
    

def toggle(dev,idx=1):
    result = run_cmd(_toggle,dev,idx)
    state = get_dps(result,idx)
    print("%s[%s] => %s" % (dev['ip'],idx,state))
    return state


def status(dev):
    result = run_cmd(tuya.status,dev)
    return result


def on(dev,idx=1):
    return run_cmd(tuya.set_state,dev,True,idx)

def off(dev,idx=1):
    return run_cmd(tuya.set_state,dev,False,idx)

def set_status(dev,data):
    return run_cmd(tuya.set_status,dev,data)


def loop():
    for i in range (0,10):
        logger.warning('Loop')
        time.sleep(0.5)
        


def async_toggle(dev,idx=1):
    ev = gevent.spawn(toggle,dev).link(result)
    #return result.get_nowait()

# if state:
#     tuya.set_status(device,{"1":False})
# else:
#     tuya.set_status(device,{"1":True,"2":'white',"3":25,"4":25})


# for i in range(25,255,5):
#     tuya.set_status(device,{"1":True,"2":'white',"3":i,"4":100})
#     time.sleep(2)

time.sleep(0.3)
#logger.info()
#logger.info(tuya.status(device))
import ac
#import pdb;pdb.set_trace()

import bpdb;bpdb.set_trace()