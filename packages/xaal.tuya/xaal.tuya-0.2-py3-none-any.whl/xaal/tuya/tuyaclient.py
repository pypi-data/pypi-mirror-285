from gevent import monkey; monkey.patch_socket();

import gevent
from decorator import decorator

import tuyaface
from tuyaface.const import CMD_TYPE

import json
import socket
import time
import colorsys
import enum


import logging
logger = logging.getLogger(__name__)
logging.getLogger('tuyaface').setLevel('INFO')


HEART_BEAT_DELAY = 7

@decorator
def spawn(func,*args,**kwargs):
    gevent.spawn(func,*args,**kwargs)


def now():
    return time.time()

class Event(enum.Enum):
    DISCONNECTED  = 0
    CONNECTED     = 1
    PONG          = 2
    DPS           = 3


class TuyaClient(object):

    def __init__(self,device):
        self.device = device
        self.ip = device['ip']
        self.sock = None
        self.connected = False
        self.last_send = 0
        self.last_recv = 0
        self.request_cnt = 0 
        self.warning_mitigation = -1
        self.dps_query = CMD_TYPE.DP_QUERY
        self.subscribers = []

    def start(self):
        # no need to call connect() here. The connection monitoring will.
        self.monitor_connection()
        self.push()
        self.pull()
        
    def subscribe(self,func):
        self.subscribers.append(func)

    def pubish(self,ev_type,ev_data=None):
        for k in self.subscribers:
            k(ev_type,ev_data)

    def connect(self):        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sock.connect((self.ip, 6668))
            self.sock.settimeout(10)
            self.connected = True
            self.last_send = 0
            logger.warning(f"Connected to: {self.ip}")
            self.pubish(Event.CONNECTED)
        except Exception as ex:
            if self.warning_mitigation != self.last_recv:
                logger.warning(f"Unable to connect {self.ip}: {ex}")
                self.warning_mitigation = self.last_recv
            
    def send(self,command,payload=None):
        request = tuyaface._generate_payload(self.device, command, payload, self.request_cnt)
        try:
            self.last_send = now()
            self.sock.send(request)
            return True
        except Exception as ex:
            logger.warning(f"Unable to send data to {self.ip}: {ex}")
            self.network_error()
            return False

    def receive(self):
        try:
            data = self.sock.recv(4096)
            result = list(tuyaface._process_raw_reply(self.device, data))
            self.last_recv = now()
            return result
        except Exception as ex:
            logger.warning(f"Unable to receive from {self.ip}: {ex}")
            self.network_error()

    def network_error(self):
        if self.connected:
            self.pubish(Event.DISCONNECTED)
        self.connected = False


    #========================================================================
    # DPS Handling / parse / query / post
    #========================================================================
    def fix_buggy_dp_query(self):
        # some devices anwsers 'json obj data unvalid' to DP_QUERY
        # so we switch to CONTROL_NEW and send another request
        self.dps_query = CMD_TYPE.CONTROL_NEW
        self.request_dps()

    def parse_payload(self,payload):
        cmd = payload.get('cmd',-1)
        if cmd == CMD_TYPE.HEART_BEAT:
            #self.pubish(Event.PONG)
            pass
        elif cmd in [CMD_TYPE.DP_QUERY,CMD_TYPE.STATUS,CMD_TYPE.CONTROL,CMD_TYPE.CONTROL_NEW]:
            data = payload.get('data',{})
            if data == 'json obj data unvalid':
                self.fix_buggy_dp_query()
            elif data in ['',None]:
                return
            else:
                try:
                    dps = json.loads(data).get('dps',{})
                except json.decoder.JSONDecodeError:
                    logger.warning(f"JSON Error: {data} ")
                else:
                    self.pubish(Event.DPS,dps)
        else:
            logger.info(f"{self.ip} =>{payload}")

    def request_dps(self):
        """Query the devie DPS, retrun True if Ok, False if trouble"""
        if self.connected:
            self.request_cnt +=1
            return self.send(self.dps_query)
        return False

    def post_dps(self,dps):
        """Send given dps to the device. Return True if Ok, False if trouble"""
        if self.connected:
            self.request_cnt +=1
            tmp = {str(k): v for k, v in dps.items()}
            return self.send(CMD_TYPE.CONTROL,tmp)
        return False

    #========================================================================
    # Coroutines here
    #========================================================================
    @spawn
    def monitor_connection(self):
        """ Monitor the socket state and call connect if something is wrong"""
        while 1:
            if self.connected == False:
                if self.sock:
                    self.sock.close()
                    gevent.sleep(3)
                self.connect()
                gevent.sleep(0.5)
            gevent.sleep(0.1)

    @spawn
    def pull(self):
        """Pull replies from device, and parseit"""
        while 1:
            if self.connected:
                data = self.receive()
                if data == None:
                    continue
                for k in data:
                    self.parse_payload(k)
            else:
                gevent.sleep(0.1)

    @spawn
    def push(self):
        """ Send device HB, and monitor stalled cnx"""
        while 1:
            # nothing to do since not connected
            if not self.connected:
                gevent.sleep(0.1)
                continue

            now_ = now()
            # some sec since last send and nothing arise => cnx is stalled
            if  (now_ > self.last_send + 3) and (self.last_recv < self.last_send):
                logger.warning(f"Connexion stalled {self.ip}")
                self.last_send = 0
                self.network_error()
                continue

            # nothing received since HEART_BEAT_DELAY, it's time to send a ping
            if now_ > self.last_recv + HEART_BEAT_DELAY:
                # ensure we wait 2 sec to send a second one
                if now_ > self.last_send + 2:
                    self.send(CMD_TYPE.HEART_BEAT)
                    continue
            
            gevent.sleep(0.1)



def color_to_hex(hsv):
    """
    Converts the hsv list in a hexvalue.

    Args:
        hue is 0 to 360, sat & brighness between 0 to 1"
    """
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

def hexvalue_to_hsv(hexvalue):
    """
    Converts the hexvalue used by tuya for colour representation into
    an HSV value.

    Args:
        hexvalue(string): The hex representation generated by BulbDevice._rgb_to_hexvalue()
    """
    h = int(hexvalue[7:10], 16)
    s = int(hexvalue[10:12], 16) / 255
    v = int(hexvalue[12:14], 16) / 255
    return (h, s, v)




def evt_test(ev_type,ev_data):
    if ev_type != Event.PONG:
        print(f"New event {Event(ev_type)} {ev_data}")

def launch(dev):
    c = TuyaClient(dev)
    c.start()
    c.subscribe(evt_test)
    return c


def test():
    import coloredlogs
    coloredlogs.install('DEBUG')
    from gevent.backdoor import BackdoorServer

    clients = []
    # lamp LSC
    d1 = {  'ip' : '192.168.1.65', 'deviceid' : 'bf017829869d45e15dld7g','localkey' : '7568ee8fdbc4e232', 'protocol' : '3.3' }
    # SHP6-test
    d2 = {  'ip' : '192.168.1.63','deviceid' : '142200252462ab419539','localkey' : '6eeec6c9eeeff233','protocol' : '3.3'}
    # alĥaplug-2
    d3 = {  'ip' : '192.168.1.61','deviceid' : '74012545dc4f229f058f','localkey' : 'e3e182a7491f2d44','protocol' : '3.3'}
    # shp-7
    d4 = {  'ip' : '192.168.1.66', 'deviceid' : '42361312d8f15bd5a25d','localkey' : 'af6430180fd6dde7', 'protocol' : '3.3' }
    # LSC Edison
    d5 = {  'ip' : '192.168.1.172', 'deviceid' : '40005734840d8e4d5500','localkey' : 'b0bd409134204b59', 'protocol' : '3.3' }
    # utorch rgb
    d6 = {  'ip' : '192.168.1.162', 'deviceid' : '00747018f4cfa262ea13','localkey' : 'f598419fef804b7f', 'protocol' : '3.3' }
    # buggy
    d0 = {  'ip' : '192.168.1.50', 'deviceid' : '42361312d8f15bd5a25d','localkey' : 'af6430180fd6dde7', 'protocol' : '3.3' }

    try:
        clients.append(launch(d1))
        clients.append(launch(d2))
        clients.append(launch(d3))
        clients.append(launch(d4))
        #clients.append(launch(d6))
        clients.append(launch(d5))

        server = BackdoorServer(('127.0.0.1', 5001),banner="TuyaClient",locals={'c': clients,'CMD_TYPE': CMD_TYPE})
        server.serve_forever()

        #gevent.wait()
    except KeyboardInterrupt:
        for k in clients:
            k.sock.close()
        #import pdb;pdb.set_trace()


if __name__ == '__main__':
    test()


