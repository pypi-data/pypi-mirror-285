import logging
from xaal.schemas import devices
from xaal.lib import tools

from .bindings import funct
from functools import partial

logger = logging.getLogger(__name__)


class KNXDev:
    def __init__(self, gw, cfg):
        # print(extract_classname(self))
        self.gateway = gw
        self.cfg = cfg
        self.attributes_binding = {}
        # search for xaal address, if None, the device will produce a new one
        self.addr = tools.get_uuid(cfg.get('addr', None))
        if self.addr == None:
            self.addr = tools.get_random_uuid()
            cfg['addr'] = str(self.addr)
            gw.save_config = True
        self.dev = None
        self.setup()

    def setup(self):
        logger.warn("Please define setup() in this device")

    def write(self, group_addr, dpt, data):
        """ return a function to be call to write the data to right group_addr """
        func = partial(self.gateway.knx.write, group_addr, data, dpt)
        return func

    def bind_attribute(self, attribute, group_addr, func, dpt):
        """ bind a group_addr to a xaal attribute, and apply the func """
        ptr = partial(func, attribute, dpt, data=None)
        self.attributes_binding.update({group_addr: ptr})

    def parse(self, cemi):
        if cemi.group_addr in self.attributes_binding:
            func = self.attributes_binding[cemi.group_addr]
            func(data=cemi.data)

# =============================================================================
# PowerRelay / Lamp ..
# =============================================================================


class OnOffMixin:
    def setup_onoff(self, state_attribute):
        cmd = self.cfg.get('cmd', None)
        if cmd:
            self.dev.add_method('turn_on', self.write(cmd, '1', 1))
            self.dev.add_method('turn_off', self.write(cmd, '1', 0))
        state = self.cfg.get('state', None) or cmd
        mod = self.cfg.get('mod', 'bool')
        if state:
            self.bind_attribute(state_attribute, state, funct[mod], '1')
        self.dev.info = "KNX %s" % cmd or state


class PowerRelay(KNXDev, OnOffMixin):
    def setup(self):
        self.dev = devices.powerrelay(self.addr)
        self.setup_onoff(self.dev.get_attribute("power"))


class PowerRelayToggle(KNXDev, OnOffMixin):
    def setup(self):
        self.dev = devices.powerrelay_toggle(self.addr)
        self.setup_onoff(self.dev.get_attribute("power"))
        toggle = self.cfg.get('toggle', None)
        if toggle:
            self.dev.add_method('toggle', self.write(toggle, '1', 1))


class Lamp(KNXDev, OnOffMixin):
    def setup(self):
        self.dev = devices.lamp(self.addr)
        self.setup_onoff(self.dev.get_attribute("light"))


class LampToggle(KNXDev, OnOffMixin):
    def setup(self):
        self.dev = devices.lamp_toggle(self.addr)
        self.setup_onoff(self.dev.get_attribute("light"))
        toggle = self.cfg.get('toggle', None)
        if toggle:
            self.dev.add_method('toggle', self.write(toggle, '1', 1))


class Switch(KNXDev):
    def setup(self):
        self.dev = devices.switch(self.addr)
        state = self.cfg.get('state', None)
        if state:
            self.bind_attribute(self.dev.get_attribute('position'), state, funct['bool'], '1')
            self.dev.info = "KNX %s" % state


class Shutter(KNXDev):
    def setup(self):
        self.dev = devices.shutter(self.addr)
        up_down = self.cfg.get('updown_cmd', None)
        stop = self.cfg.get('stop_cmd', None)
        if up_down:
            self.dev.add_method('up', self.write(up_down, '1', 0))
            self.dev.add_method('down', self.write(up_down, '1', 1))
        if stop:
            self.dev.add_method('stop', self.write(stop, '1', 1))


class ShutterPosition(KNXDev):
    def setup(self):
        self.dev = devices.shutter_position(self.addr)
        up_down = self.cfg.get('updown_cmd', None)
        stop = self.cfg.get('stop_cmd', None)
        position = self.cfg.get('position_cmd', None)
        if up_down:
            self.dev.add_method('up', self.write(up_down, '1', 0))
            self.dev.add_method('down', self.write(up_down, '1', 1))
        if stop:
            self.dev.add_method('stop', self.write(stop, '1', 1))
        if position:
            self.dev.add_method('position', self.write(position, '1', 1))


# =============================================================================
# Sensors
# =============================================================================
class PowerMeter(KNXDev):
    def setup(self):
        self.dev = devices.powermeter(self.addr)
        self.dev.unsupported_attributes = ['devices']
        self.dev.del_attribute(self.dev.get_attribute('devices'))
        power = self.cfg.get('power', None)
        p_dpt = self.cfg.get('power_dpt', '9')
        p_mod = self.cfg.get('power_mod', 'set')
        if power:
            self.bind_attribute(self.dev.get_attribute('power'), power, funct[p_mod], p_dpt)
        else:
            self.dev.del_attribute(self.dev.get_attribute('power'))
        energy = self.cfg.get('energy', None)
        e_dpt = self.cfg.get('energy_dpt', '13')
        e_mod = self.cfg.get('energy_mod', 'set')
        if energy:
            self.bind_attribute(self.dev.get_attribute('energy'), energy, funct[e_mod], e_dpt)
        else:
            self.dev.del_attribute(self.dev.get_attribute('energy'))
        self.dev.info = "KNX %s" % (power or energy)


class Thermometer(KNXDev):
    def setup(self):
        self.dev = devices.thermometer(self.addr)
        temperature = self.cfg.get('temperature', None)
        t_dpt = self.cfg.get('temperature_dpt', '9')
        t_mod = self.cfg.get('temperature_mod', 'set')
        if temperature:
            self.bind_attribute(self.dev.get_attribute('temperature'), temperature, funct[t_mod], t_dpt)
        self.dev.info = "KNX %s" % temperature


class Hygrometer(KNXDev):
    def setup(self):
        self.dev = devices.hygrometer(self.addr)
        humidity = self.cfg.get('humidity', None)
        h_dpt = self.cfg.get('humidity_dpt', '5.001')
        h_mod = self.cfg.get('humidity_mod', 'round')
        if humidity:
            self.bind_attribute(self.dev.get_attribute('humidity'), humidity, funct[h_mod], h_dpt)
        self.dev.info = "KNX %s" % humidity


class CO2Meter(KNXDev):
    def setup(self):
        self.dev = devices.co2meter(self.addr)
        co2 = self.cfg.get('co2', None)
        c_dpt = self.cfg.get('co2_dpt', '9')
        c_mod = self.cfg.get('co2_mod', 'round')
        if co2:
            self.bind_attribute(self.dev.get_attribute('co2'), co2, funct[c_mod], c_dpt)
        self.dev.info = "KNX %s" % co2


class Luxmeter(KNXDev):
    def setup(self):
        self.dev = devices.luxmeter(self.addr)
        illuminance = self.cfg.get('illuminance', None)
        l_dpt = self.cfg.get('illuminance_dpt', '7')
        l_mod = self.cfg.get('illuminance_mod', 'set')
        if illuminance:
            self.bind_attribute(self.dev.get_attribute('illuminance'), illuminance, funct[l_mod], l_dpt)
        self.dev.info = "KNX %s" % illuminance


class Lightgauge(KNXDev):
    def setup(self):
        self.dev = devices.lightgauge(self.addr)
        brightness = self.cfg.get('brightness', None)
        b_dpt = self.cfg.get('brightness_dpt', '5.001')
        b_mod = self.cfg.get('brightness_mod', 'round')
        if brightness:
            self.bind_attribute(self.dev.get_attribute('brightness'), brightness, funct[b_mod], b_dpt)
        self.dev.info = "KNX %s" % brightness


class Motion(KNXDev):
    def setup(self):
        self.dev = devices.motion(self.addr)
        state = self.cfg.get('state', None)
        if state:
            self.bind_attribute(self.dev.get_attribute('presence'), state, funct['bool'], '1')
        self.dev.info = "KNX %s" % state
