from xaal.schemas import devices

import logging
import colorsys
import asyncio

logger = logging.getLogger(__name__)


def find_class(meross_dev):
    if meross_dev.type == 'msl430':
        return RGBLamp
    return None


class MerossDev(object):
    def __init__(self, meross_dev, base_addr):
        self.meross = meross_dev
        self.base_addr = base_addr
        self.embs = []
        self.setup()
        self.setup_xaal()
        logger.info(f"Found {self}")

    def setup(self):
        logger.warning('Please overide setup()')

    def setup_xaal(self):
        for dev in self.embs:
            dev.vendor_id = 'Meross'
            dev.product_id = f"{self.meross.type} HW:{self.meross.hardware_version} FW:{self.meross.firmware_version}"
            dev.info = self.meross.name
            dev.hw_id = self.meross.uuid


class RGBLamp(MerossDev):

    temp_min = 2700
    temp_max = 6500

    def setup(self):
        dev = devices.lamp_color(self.base_addr + 1)
        dev.methods['turn_on'] = self.turn_on
        dev.methods['turn_off'] = self.turn_off
        dev.methods['toggle'] = self.toggle
        dev.methods['set_brightness'] = self.set_brightness
        dev.methods['set_hsv'] = self.set_hsv
        dev.methods['set_white_temperature'] = self.set_white_temperature
        dev.methods['set_mode'] = self.set_mode
        dev.attributes['hsv'] = [0, 0, 0]
        dev.unsupported_attributes = ['scene']
        dev.unsupported_methods = ['get_scene', 'set_scene']
        dev.del_attribute(dev.get_attribute('scene'))
        self.embs.append(dev)

    async def update(self):
        # await self.meross.async_update()
        dev = self.embs[0]
        dev.attributes['light'] = self.meross.is_on()
        dev.attributes['brightness'] = self.meross.get_luminance()
        temp = (self.temp_max - self.temp_min) / 100 * self.meross.get_color_temperature() + self.temp_min
        dev.attributes['white_temperature'] = round(temp/100, 1) * 100
        rgb = self.meross.get_rgb_color()
        hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        h = round(hsv[0] * 360)
        s = round(hsv[1], 2)
        v = round(hsv[2], 2)
        dev.attributes['hsv'] = [h, s, v]
        await asyncio.sleep(0)

    async def turn_on(self):
        await self.meross.async_turn_on()
        await self.update()

    async def turn_off(self):
        await self.meross.async_turn_off()
        await self.update()

    async def toggle(self):
        await self.meross.async_toggle()
        await self.update()

    async def set_brightness(self, _brightness, _smooth=None):
        val = int(_brightness)
        await self.meross.async_set_light_color(luminance=val)
        await self.update()

    async def set_hsv(self, _hsv, _smooth=None):
        # FIXME
        if isinstance(_hsv, str):
            hsv = [float(k) for k in list(_hsv.split(','))]
        else:
            hsv = _hsv
        h, s, v = hsv
        rgb = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/360.0, s, v))
        # meross API fail to detect when light is off and set_light_color() is called
        # set_light_color() will turn light on but the API think it is still off
        # so turn it on first
        if self.embs[0].attributes['light'] == False:
            await self.meross.async_turn_on()
        await self.meross.async_set_light_color(rgb=rgb)
        await self.update()
        self.embs[0].attributes['mode'] = 'color'

    async def set_white_temperature(self, _white_temperature):
        temp = int(_white_temperature)
        value = int((temp - self.temp_min) / (self.temp_max - self.temp_min) * 100)
        if value <= 1: value = 1
        if value >= 100: value = 100
        await self.meross.async_set_light_color(temperature=value)
        await self.update()
        self.embs[0].attributes['mode'] = 'white'

    async def set_mode(self, _mode):
        dev = self.embs[0]
        if _mode == 'color':
            await self.set_hsv(dev.attributes['hsv'])
        if _mode == 'white':
            await self.set_white_temperature(dev.attributes['white_temperature'])
