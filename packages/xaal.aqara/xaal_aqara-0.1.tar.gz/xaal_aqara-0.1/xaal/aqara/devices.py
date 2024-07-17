import colorsys
from xaal.schemas import devices
from xaal.lib import Device

import json
import logging
import socket
import binascii

from Cryptodome.Cipher import AES

GW_PORT = 9898
AQARA_ENCRYPT_IV = b'\x17\x99\x6d\x09\x3d\x28\xdd\xb3\xba\x69\x5a\x2e\x6f\x58\x56\x2e'

logger = logging.getLogger(__name__)

BATTERY_LESS = ['lumi.ctrl_dualchn', 'gateway']


def find_device_class(model):
    if model in ['sensor_switch.aq3', 'sensor_switch.aq2', 'switch', '86sw1']:
        return Switch
    if model in ['86sw2', 'remote.b286acn01', 'remote.b286acn02']:
        return Switch86sw2
    if model == 'gateway':
        return Gateway
    if model == 'weather.v1':
        return Weather
    if model == 'motion':
        return Motion
    if model == 'sensor_motion.aq2':
        return MotionAQ2
    if model in ['magnet', 'sensor_magnet.aq2']:
        return Magnet
    if model == 'vibration':
        return Vibration
    if model == 'sensor_cube.aqgl01':
        return Cube
    if model == 'sensor_wleak.aq1':
        return WaterLeak
    if model == 'lumi.ctrl_dualchn':
        return RelayController
    if model == 'sensor_ht':
        return SensorHT
    return None


class AqaraDev(object):
    def __init__(self, sid, model, base_addr, xaal_gw):
        self.sid = sid
        self.model = model
        self.base_addr = base_addr
        self.xaal_gw = xaal_gw
        # xAAL embeded devices
        self.devices = [] 
        logger.info(f"Loading AqaraDevice {model} {sid}")
        self.setup()
        self.add_battery()
        self.init_properties()

    def setup(self):
        logger.warning(f"Please overide setup() in {self.__class__}")

    def add_battery(self):
        self.battery = None
        if self.model in BATTERY_LESS:
            return
        if len(self.devices) != 0:
            addr = self.devices[-1].address + 1
            bat = devices.battery(addr)
            bat.attributes['devices'] = [dev.address for dev in self.devices]
            self.devices.append(bat)
            self.battery = bat

    def init_properties(self):
        for dev in self.devices:
            dev.vendor_id = 'Xiaomi / Aqara'
            dev.product_id = self.model
            dev.hw_id = self.sid
            dev.info = f"{self.model} / {self.sid}"
            if len(self.devices) > 1:
                dev.group_id = self.base_addr + 0xff

    def parse(self,pkt):
        cmd = pkt.get('cmd', None)
        if not cmd:
            logger.warning('pkt w/ no command: %s' % pkt)
            return
        if cmd in ['report', 'heartbeat']:
            pload = pkt.get('data', None)
            if pload:
                # json in json really ? grr
                data = json.loads(pload)
                if cmd == 'report':
                    self.on_report(data)
                if cmd == 'heartbeat':
                    self.on_heartbeat(data)
        elif cmd in ['iam']:
            self.on_iam(pkt)
        else:
            logger.info(pkt)

    def parse_voltage(self, data):
        # https://github.com/home-assistant/core/blob/e63e8b6ffe627dce8ee7574c652af99267eb7376/homeassistant/components/xiaomi_aqara/__init__.py#L355
        if not self.battery:
            return
        val = data.get('voltage', None)
        if val:
            voltage = int(val)
            max_volt = 3300
            min_volt = 2800
            voltage = min(voltage, max_volt)
            voltage = max(voltage, min_volt)
            percent = ((voltage - min_volt) / (max_volt - min_volt)) * 100
            self.battery.attributes['level'] = int(percent)

    def on_report(self, data):
        logger.info('Unhandled report %s' % data)

    def on_heartbeat(self, data):
        self.parse_voltage(data)
        self.on_report(data)

    def report(self, data):
        # data sent by the hub not the device
        self.parse_voltage(data)
        self.on_report(data)

    def on_iam(self, data):
        logging.info('Unhandled iam %s' % data)


class Switch(AqaraDev):
    def setup(self):
        dev = devices.button(self.base_addr)
        self.devices.append(dev)

    def on_report(self, data):
        status = data.get('status', None)
        if status:
            self.devices[0].send_notification(status)


class Switch86sw2(AqaraDev):
    def setup(self):
        btn1 = devices.button(self.base_addr)
        btn2 = devices.button(self.base_addr+1)
        btn3 = devices.button(self.base_addr+2)
        self.devices = self.devices + [btn1, btn2, btn3]

    def on_report(self,data):
        chans = ['channel_0', 'channel_1', 'dual_channel']
        idx = 0
        for k in chans:
            r = data.get(k, None)
            # in the current firmware this switch always return both click and long_click
            if r and (r.startswith('long_') == False):
                if r == 'both_click':
                    r = 'click'
                self.devices[idx].send_notification(r)
            idx = idx + 1

class Weather(AqaraDev):
    def setup(self):
        self.devices.append(devices.thermometer(self.base_addr))
        self.devices.append(devices.hygrometer(self.base_addr+1))
        self.devices.append(devices.barometer(self.base_addr+2))

    def on_report(self,data):
        val = data.get('temperature', None)
        if val: self.devices[0].attributes['temperature'] = round(int(val) / 100.0,1)
        val = data.get('humidity', None)
        if val: self.devices[1].attributes['humidity'] = round(int(val) / 100.0,1)
        val = data.get('pressure', None)
        if val: self.devices[2].attributes['pressure'] = round(int(val) / 100.0,1)

# MC 24/09/2019
class SensorHT(AqaraDev):
    def setup(self):
        self.devices.append(devices.thermometer(self.base_addr))
        self.devices.append(devices.hygrometer(self.base_addr+1))

    def on_report(self,data):
        val = data.get('temperature', None)
        if val: self.devices[0].attributes['temperature'] = round(int(val) / 100.0,1)
        val = data.get('humidity', None)
        if val: self.devices[1].attributes['humidity'] = round(int(val) / 100.0,1)


class Motion(AqaraDev):
    def setup(self):
        self.devices.append(devices.motion(self.base_addr))
        
    def on_report(self,data):
        # motion
        val = data.get('status',None)
        if val and val == 'motion':
            self.devices[0].attributes['presence'] = True
        val = data.get('no_motion',None)
        if val:
            self.devices[0].attributes['presence'] = False

class MotionAQ2(Motion):
    def setup(self):
        Motion.setup(self)
        self.devices.append(devices.luxmeter(self.base_addr+1))

    def on_report(self, data):
        Motion.on_report(self, data)
        val = data.get('lux', None)
        if val:
            self.devices[1].attributes['illuminance'] = int(val)

class Magnet(AqaraDev):
    def setup(self):
        dev = devices.contact(self.base_addr)
        self.devices.append(dev)

    def on_report(self, data):
        status = data.get('status', None)
        if status and status == 'open':
            self.devices[0].attributes['detected'] = True
        if status and status == 'close':
            self.devices[0].attributes['detected'] = False


class Vibration(AqaraDev):pass


class Cube(AqaraDev):pass

class RelayController(AqaraDev):pass

class WaterLeak(AqaraDev):
    # no device yet on this

    def on_report(self, data):
        status = data.get('status', None)
        if status and status == 'leak':
            logger.warning('Leaking..')
        if status and status == 'no_leak':
            logger.warning('No leaking')


UDP_MAX_SIZE=65507


class Gateway(AqaraDev):
    def setup(self):
        self.sids = []
        self.ip = None
        self.token = None
        self.ready = False
        self._rgb = None
        self._secret = None
        self.connect()
        lamp = devices.lamp_color(self.base_addr)
        lamp.methods['turn_on'] = self.lamp_on
        lamp.methods['turn_off'] = self.lamp_off
        lamp.methods['toggle'] = self.lamp_toggle
        # lamp.methods['debug'] = self.debug
        lamp.methods['set_hsv'] = self.set_hsv
        lamp.methods['set_brightness'] = self.set_brightness
        # The gateway only support RGB, no white
        lamp.attributes['mode'] = 'color'
        lamp.unsupported_methods = ['set_mode', 'set_white_temperature', 'set_scene']

        unused_attrs = ['white_temperature', 'scene']
        for k in unused_attrs:
            attr = lamp.get_attribute(k)
            lamp.del_attribute(attr)

        lamp.unsupported_attributes = unused_attrs
        self.devices.append(lamp)

        siren = Device('siren.sound', self.base_addr + 1)
        siren.methods['play'] = self.siren_play
        siren.methods['stop'] = self.siren_stop
        siren.methods['debug'] = self.debug
        self.devices.append(siren)

        lux = devices.luxmeter(self.base_addr+2)
        self.devices.append(lux)

    def debug(self):
        import pdb; pdb.set_trace()

    @property
    def rgb(self):
        """ At boot, we didn't receive the rbg value yet (have to toggle on/off), 
        without this value, we are unable to set_hsv (unknow brightness) or set_brightness
        (unknow color). So, if we don't know the value, simply think it's red.
        """
        if self._rgb == None:
            return self.rgb_to_value(255, 10, 10)
        return self._rgb

    @rgb.setter
    def rgb(self, value):
        self._rgb = value

    #========================================================================
    ## GW Unicast methods
    #========================================================================  
    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, value):
        logger.debug('Seting GW secret to %s' % value)
        self._secret = value.encode('utf-8')

    def make_key(self):
        cipher = AES.new(self.secret, AES.MODE_CBC, IV=AQARA_ENCRYPT_IV)
        return binascii.hexlify(cipher.encrypt(self.token)).decode("utf-8")

    def connect(self):
        """ prepare the unicast socket"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)

    def send(self, pkt):
        """send a the unicast datagram to the lumi GW"""
        if not self.ip:
            logger.warning("GW IP not found yet, please wait")
            return
        try:
            self.sock.sendto(pkt, (self.ip, GW_PORT))
            ans = self.sock.recv(UDP_MAX_SIZE)
            return ans
        except Exception as e:
            logger.warning(e)

    def send_cmd(self, cmd, sid, data=None):
        """ craft the datagram pkt and send to the lumi gw"""
        if not data:
            data = {}

        if not self.token:
            logger.warning("No token yet, please wait")
            return
        if not self.secret:
            logger.warning("Please set the secret key in cfg file")
            return
        key = self.make_key()
        data.update({"key": key})
        pload = {"cmd":   cmd,
                 "sid":   sid,
                 "data":  data
                }
        pkt = json.dumps(pload).encode('utf8')
        return self.send(pkt)


    #========================================================================
    ## Gateway Unicast commands
    #========================================================================  
    def write(self, data = None):
        """send command to the GW, used for siren, lamp, radio?"""
        if not data:
            data = {}
        pkt = self.send_cmd("write", self.sid, data)
        self.on_receive(pkt)

    def get_id_list(self):
        """ retreive the devices list"""
        pkt = self.send_cmd("get_id_list", self.sid)
        self.on_receive(pkt)

    def discover(self):
        """
        query device list and ask for a read, on each sid

        The doc say we should use {"cmd": "discovery"} instead of get_id_list + 
        read, but I always have a discory error => "missing sid"
        http://docs.opencloud.aqara.com/en/development/gateway-LAN-communication/
        """
        self.get_id_list()
        for sid in self.sids:
            pkt = self.send_cmd("read", sid)
            self.on_receive(pkt)

    def on_receive(self, pkt):
        if not pkt:
            return

        pload = json.loads(pkt)
        cmd = pload.get('cmd', None)

        if cmd == 'get_id_list_ack':
            data = pload.get('data', '[]')
            self.sids = json.loads(data)

        if cmd == 'read_ack':
            model = pload.get('model', None)
            sid = pload.get('sid', None)
            dev = self.xaal_gw.get_device(sid, model)
            if dev:
                data = json.loads(pload.get('data', '{}'))
                dev.report(data)
            else:
                logger.warning("Unknow device %s" % pload)

        if cmd == 'write_ack':
            # some gateway report states after a write write_ack
            logger.debug(pkt)
            data = json.loads(pload.get('data', '{}'))
            self.report(data)

    #========================================================================
    ## RGB Leds 
    #========================================================================
    def rgb_to_value(self, red, green, blue, brightness=0xFF):
        return brightness << 24 | (red << 16) | (green << 8) | blue

    def value_to_rgb(self, value):
        brightness = (value >> 24) & 0xFF
        r = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return (r, g, b, brightness)

    def update_color(self):
        lamp = self.devices[0]
        rgb = self.value_to_rgb(self.rgb)

        r = rgb[0] / 255.0
        g = rgb[1] / 255.0
        b = rgb[2] / 255.0
        brightness = rgb[3]

        hsv = colorsys.rgb_to_hsv(r, g, b)
        h = round(hsv[0] * 360)
        s = round(hsv[1], 2)
        v = round(hsv[2], 2)
        lamp.attributes['hsv'] = [h, s, v]
        lamp.attributes['brightness'] = brightness

    def set_hsv(self, _hsv, _smooth=None):
        # FIXME
        if isinstance(_hsv,str):
            hsv = [float(k) for k in list(_hsv.split(','))]
        else:
            hsv = _hsv
        h,s,v = hsv
        rgb = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/360.0, s, v))
        brightness = self.value_to_rgb(self.rgb)[3]
        value = self.rgb_to_value(*rgb, brightness)
        self.lamp_set(value)

    def set_brightness(self, _brightness, _smooth=None):
        brightness = int(_brightness)
        rgb = self.value_to_rgb(self.rgb)[0:3]
        value = self.rgb_to_value(*rgb, brightness)
        self.lamp_set(value)

    def lamp_set(self, value):
        data = {"rgb": value}
        self.write(data)

    def lamp_on(self):
        self.lamp_set(self.rgb)

    def lamp_off(self):
        self.lamp_set(0)

    def lamp_toggle(self):
        if self.devices[0].attributes['light'] == True:
            self.lamp_off()
        else:
            self.lamp_on()

    #========================================================================
    ## Siren
    #========================================================================  
    def siren_play(self, _sound=2, _volume=5):
        logger.info('Playing %s %s' % (_sound, _volume))
        data = {
                "mid": int(_sound),
                "volume": int(_volume),
                }
        self.write(data)

    def siren_stop(self):
        data = {"mid": 999}
        self.write(data)

    #========================================================================
    ## GW Mutlicast messages handlers
    #========================================================================  
    def search_ip(self, data):
        ip = data.get('ip', None)
        if ip and ip != self.ip:
            self.ip = ip
            logger.warning(f"GW IP found: {ip}")

    def parse(self, pkt):
        # extract the token before normal parsing
        token = pkt.get('token', None)
        if token:
            self.token = token.encode('utf8')
        AqaraDev.parse(self, pkt)

    def on_heartbeat(self, data):
        self.search_ip(data)
        if not self.ready:
            if self.token and self.ip:
                self.ready = True
                self.discover()

    def on_report(self, data):
        rgb = data.get('rgb', None)
        if rgb != None:
            rgb = int(rgb)
            if rgb == 0:
                self.devices[0].attributes['light'] = False
            else:
                self.devices[0].attributes['light'] = True
                self.rgb = rgb
                self.update_color()
        val = data.get('illumination', None)
        if val:
            # This value is in lm, we should map this to lux, but 
            # values doesn't seems to match
            self.devices[2].attributes['illuminance'] = int(val)

    def on_iam(self, data):
        self.search_ip(data)
