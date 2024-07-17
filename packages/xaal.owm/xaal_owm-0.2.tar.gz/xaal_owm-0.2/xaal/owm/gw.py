import platform
import logging

import pyowm
from pyowm.exceptions import OWMError
from xaal.lib import tools
from xaal.schemas import devices

from xaal.lib import helpers

PACKAGE_NAME = "xaal.owm"
RATE = 300 # update every 5 min
API_KEY = '3a5989bac31472cd41d69e92838bd454'

logger = logging.getLogger(PACKAGE_NAME)

def setup_dev(dev):
    dev.vendor_id  = "IHSEV"
    dev.product_id = "OpenWeatherMap"
    dev.info       = "%s@%s" % (PACKAGE_NAME,platform.node())
    dev.url        = "https://www.openweathermap.org"
    dev.version    = 0.3
    return dev

class GW:
    def __init__(self,engine):
        self.eng = engine
        engine.on_stop(self.save_config)
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg == None:
            logger.info('New config file')
            cfg = tools.new_cfg(PACKAGE_NAME)
            cfg['config']['base_addr'] = str(tools.get_random_base_uuid())
        self.cfg = cfg

        self.setup()
        self.update()

    def setup(self):
        """ create devices, register .."""
        cfg = self.cfg['config']
        base_addr = tools.get_uuid(cfg['base_addr'])
        # devices
        d1 = devices.thermometer(base_addr +0)
        d2 = devices.hygrometer(base_addr +1)
        d3 = devices.barometer(base_addr +2)
        d4 = devices.windgauge(base_addr +3)
        d4.unsupported_attributes.append('gust_angle')
        d4.del_attribute(d4.get_attribute('gust_angle'))
        self.devs = [d1,d2,d3,d4]

        # gw
        gw = devices.gateway(tools.get_uuid(cfg['addr']))
        gw.attributes['embedded'] = [dev.address for dev in self.devs]

        group = base_addr + 0xff
        for dev in (self.devs + [gw,]):
            setup_dev(dev)
            if dev != gw:
                dev.group_id = group

        self.eng.add_devices(self.devs + [gw,])
        # OWM stuff
        self.eng.add_timer(self.update,RATE)
        # API Key
        api_key = cfg.get('api_key',None)
        if not api_key:
            cfg['api_key'] = api_key = API_KEY
        # Place 
        self.place = cfg.get('place',None)
        if not self.place:
            cfg['place'] = self.place = 'Brest,FR'
        # We are ready
        self.owm = pyowm.OWM(api_key)

    @helpers.spawn
    def update(self):
        try:
            self._update()
        except OWMError as e:
            logger.warn(e)

    def _update(self):
        weather = self.owm.weather_at_place(self.place).get_weather()
        self.devs[0].attributes['temperature'] = round(weather.get_temperature(unit='celsius').get('temp',None),1)
        self.devs[1].attributes['humidity']    = weather.get_humidity()
        self.devs[2].attributes['pressure']    = weather.get_pressure().get('press',None)
        wind = weather.get_wind().get('speed',None)
        if wind: wind = round(wind * 3600 / 1000, 1) # m/s => km/h
        self.devs[3].attributes['wind_strength'] = wind
        self.devs[3].attributes['wind_angle'] = weather.get_wind().get('deg',None)
        self.devs[3].attributes['gust_strength'] = weather.get_wind().get('gust',None)

    def save_config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()

def setup(engine):
    gw = GW(engine)
    return True
