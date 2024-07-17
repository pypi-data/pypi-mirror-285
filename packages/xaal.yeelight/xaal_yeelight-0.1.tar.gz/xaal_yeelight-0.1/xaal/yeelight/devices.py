import colorsys
import logging
import copy
import functools
import gevent
from decorator import decorator

from xaal.schemas import devices
from xaal.lib import tools

logger = logging.getLogger(__name__)


def run(func, *args, **kwargs):
    self = args[0]
    if not self.lock.ready():
        logger.warning(f"LOCKED waiting.. {func}")
    self.lock.wait()
    self.lock.acquire()
    try:
        # logger.debug("Calling %s " % func)
        func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"{self.bulb} {e} calling {func}")
    self.lock.release()


@decorator
def spawn(func, *args, **kwargs):
    ptr = functools.partial(run, func, *args, **kwargs)
    gevent.spawn(ptr)


def properties_compare(orig, new):
    res = {}
    for k in new.keys():
        if k in orig.keys():
            if new[k] != orig[k]:
                res.update({k: new[k]})
    return res


class YeelightDev(object):
    def __init__(self, bulb, cfg):
        self.bulb = bulb
        self.cfg = cfg
        self.addr = tools.get_uuid(cfg.get('addr'))
        self.dev = None
        self.setup()
        self.set_xaal()
        logger.info(f"New device at {bulb._ip} : {self.addr}")
        # It's safer to use a lock to avoid the socket to be used w/ 2
        # greenlets at the same time. This can occurs on the device refresh
        self.lock = gevent.lock.BoundedSemaphore(1)
        # self.bulb.start_music()

    def debug_properties(self, properties):
        if not hasattr(self, 'last_properties'):
            self.last_properties = properties
            logger.debug(properties)
            return
        # for debugging only display changes
        changes = properties_compare(self.last_properties, properties)
        if changes:
            logger.debug(changes)
        self.last_properties = copy.copy(properties)

    def set_xaal(self):
        self.dev.vendor_id = 'Yeelight'
        self.dev.info = str(self.bulb)

    def setup(self):
        logger.warning('Please overide setup()')

    def on_properties(self, properties):
        logger.warning('Please overide on_properties')
        self.debug_properties(properties)

    @spawn
    def turn_on(self):
        self.bulb.duration = int(self.cfg.get('smooth_on', 200))
        self.bulb.turn_on()
        self._update_properties()

    @spawn
    def turn_off(self):
        self.bulb.duration = int(self.cfg.get('smooth_off', 200))
        self.bulb.turn_off()
        self._update_properties()

    def toggle(self):
        if self.dev.attributes['light']:
            self.turn_off()
        else:
            self.turn_on()

    @spawn
    def get_properties(self):
        self._update_properties()

    def _update_properties(self):
        properties = self.bulb.get_properties()
        self.on_properties(properties)
        # we need to be connected to find out which model
        if self.dev.product_id == None:
            self.dev.product_id = str(self.bulb.bulb_type)


class RGBW(YeelightDev):
    def setup(self):
        dev = devices.lamp_color(self.addr)
        dev.methods['turn_on'] = self.turn_on
        dev.methods['turn_off'] = self.turn_off
        dev.methods['toggle'] = self.toggle
        dev.methods['set_brightness'] = self.set_brightness
        dev.methods['set_hsv'] = self.set_hsv
        dev.methods['set_white_temperature'] = self.set_white_temperature
        dev.methods['set_mode'] = self.set_mode
        dev.info = f"RGBW / {self.addr}"
        dev.attributes['hsv'] = [0, 0, 0]
        dev.unsupported_attributes = ['scene']
        dev.unsupported_methods = ['get_scene', 'set_scene']
        self.dev = dev

    @spawn
    def set_brightness(self, _brightness, _smooth=None):
        val = int(_brightness)
        if _smooth:
            duration = int(_smooth)
        else:
            duration = int(self.cfg.get('smooth_default', 500))
        self.bulb.turn_on()
        self.bulb.duration = duration
        self.bulb.set_brightness(val)
        self._update_properties()

    @spawn
    def set_hsv_(self, _hsv, _smooth=None):
        # FIXME
        if isinstance(_hsv, str):
            hsv = [float(k) for k in list(_hsv.split(','))]
        else:
            hsv = _hsv
        h, s, v = hsv
        v = int(v * 100)
        s = int(s * 100)
        h = int(h)
        if _smooth:
            duration = int(_smooth)
        else:
            duration = int(self.cfg.get('smooth_default', 500))
        duration = max(duration, 50)
        self.bulb.turn_on()
        self.bulb.duration = duration
        self.bulb.set_hsv(h, s, v)
        gevent.sleep(0.2)
        self._update_properties()
        target = round((duration / 1000.0), 1)
        # we schedule some get_properties at the end of the flow to update the current color
        # As time drift, don't expect to have it working for a 1 hour flow.
        self.dev.engine.add_timer(self.get_properties, target, 1)
        self.dev.engine.add_timer(self.get_properties, target+0.5, 1)

    @spawn
    def set_hsv(self, _hsv, _smooth=None):
        # FIXME
        if isinstance(_hsv, str):
            hsv = [float(k) for k in list(_hsv.split(','))]
        else:
            hsv = _hsv
        h, s, v = hsv

        if _smooth:
            duration = int(_smooth)
        else:
            duration = int(self.cfg.get('smooth_default', 500))
        duration = max(duration, 50)
        self.bulb.turn_on()
        self.bulb.duration = duration

        rgb = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h / 360.0, s, v))
        self.bulb.set_rgb(rgb[0], rgb[1], rgb[2])

        gevent.sleep(0.2)
        self._update_properties()
        target = round((duration / 1000.0), 1)
        # we schedule some get_properties at the end of the flow to update the current color
        # As time drift, don't expect to have it working for a 1 hour flow.
        if duration > 1000:
            self.dev.engine.add_timer(self.get_properties, target, 1)
            self.dev.engine.add_timer(self.get_properties, target+0.5, 1)

    @spawn
    def set_white_temperature(self, _white_temperature):
        val = int(_white_temperature)
        self.bulb.turn_on()
        self.bulb.duration = int(self.cfg.get('smooth_default', 500))
        self.bulb.set_color_temp(val)
        self._update_properties()

    def set_mode(self, _mode):
        # no need to spwan here, because it's a simple switch
        # bulb has to be 'on'. If not, we don't receive the bulb properties updates
        if _mode == 'color':
            self.set_hsv(self.dev.attributes['hsv'])
        if _mode == 'white':
            self.set_white_temperature(self.dev.attributes['white_temperature'])

    def on_properties(self, props):
        self.debug_properties(props)
        attrs = self.dev.attributes
        # light state
        power = props.get('power', None)
        if power:
            if power == 'on' : attrs['light'] = True
            if power == 'off': attrs['light'] = False
        # color mode ? 
        mode = props.get('color_mode', None)
        if mode:
            if mode == '2' : attrs['mode'] = 'white'
            if mode == '1' : attrs['mode'] = 'color'
        # white temp
        ct = props.get('ct', None)
        if ct:
            attrs['white_temperature'] = int(ct)
        # color / dimmer ?
        bright = props.get('current_brightness', None)
        rgb = props.get('rgb', None)

        if bright:
            attrs['brightness'] = int(bright)
            # hsv = list(attrs['hsv'])
            # hsv[2] = round(int(bright)/100.0, 2)
            # attrs['hsv'] = hsv
            
        # Yeelight Python API provide both rgb and hsv values
        # we parse both, even if we don't' issue set_hsv
        # sat ?
        # sat = props.get('sat',None)
        # if sat:
        #     hsv = attrs['hsv']
        #     hsv[1] = (int(sat) / 100.0)
        #     attrs['hsv']=list(hsv)
        # hue
        # hue = props.get('hue',None)
        # if hue:
        #     hsv = list(attrs['hsv'])
        #     hsv[0] = int(hue)
        #     attrs['hsv']=hsv

        if rgb:
            rgb = int(rgb)
            r = (rgb >> 16) / 255
            g = ((rgb >> 8) & 0xFF) / 255
            b = (rgb & 0xFF) / 255

            hsv = colorsys.rgb_to_hsv(r, g, b)
            h = round(hsv[0] * 360)
            s = hsv[1]
            v = hsv[2]
            attrs['hsv'] = [h, s, v]
            # attrs['brightness'] = int(hsv[2] * 100)
