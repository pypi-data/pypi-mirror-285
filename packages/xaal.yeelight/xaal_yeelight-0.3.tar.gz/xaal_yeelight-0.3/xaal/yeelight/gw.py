from gevent import monkey; monkey.patch_all(thread=False)


from xaal.lib import tools
from . import devices

import yeelight
import atexit
import logging

PACKAGE_NAME = 'xaal.yeelight'
logger = logging.getLogger(PACKAGE_NAME)

# disable internal logging
logging.getLogger("yeelight").setLevel(logging.WARNING)


class GW(object):
    def __init__(self, engine):
        self.engine = engine
        self.devices = []
        atexit.register(self._exit)
        self.config()
        self.setup()
        self.refresh()
        self.engine.add_timer(self.refresh, 60)

    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg = tools.new_cfg(PACKAGE_NAME)
            cfg['devices'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg

    def setup_(self):
        logger.info("Searching for bulbs")
        bulbs = yeelight.discover_bulbs()
        cfg = self.cfg['devices']
        for k in bulbs:
            tmp = cfg.get(k['ip'], None)
            addr = None
            if tmp:
                addr = tools.get_uuid(tmp.get('addr', None))
            if not addr:
                addr = tools.get_random_uuid()
                cfg[k['ip']] = {'addr': str(addr)}
            bulb = yeelight.Bulb(k['ip'], k['port'])
            dev = devices.RGBW(bulb, cfg[k])
            self.engine.add_device(dev.dev)

    def setup(self):
        logger.info("Loading bulbs")
        cfg = self.cfg['devices']
        for k in cfg:
            tmp = cfg.get(k, None)
            addr = None
            if tmp:
                addr = tools.get_uuid(tmp.get('addr', None))
            if not addr:
                addr = tools.get_random_uuid()
                cfg[k['ip']] = {'addr': str(addr)}
            bulb = yeelight.Bulb(k)
            dev = devices.RGBW(bulb, cfg[k])
            self.devices.append(dev)
            self.engine.add_device(dev.dev)

    def refresh(self):
        for dev in self.devices:
            dev.get_properties()
            dev.set_xaal()

    def _exit(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()


def setup(eng):
    GW(eng)
    return True
