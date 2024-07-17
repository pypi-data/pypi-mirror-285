
import aiohttp
from xaal.lib import tools
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager


from . import bindings

import logging

PACKAGE_NAME = 'xaal.meross'
logger = logging.getLogger(PACKAGE_NAME)

# disable internal logging
logging.getLogger("meross_iot").setLevel(logging.WARNING)

class GW(object):
    def __init__(self,engine):
        self.engine = engine
        self.devices = []
        self.config()
        engine.on_start(self.setup)
        engine.on_stop(self._exit)
         # refresh devices state
        engine.add_timer(self.refresh,60)
        # dis
        engine.add_timer(self.discover,60)
        
    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['config'] = {'addr': tools.get_random_uuid(),'login':'','password':''}
            cfg['devices'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg
    
    async def setup(self):
        config = self.cfg.get('config', {})
        login = config.get('login', None)
        passwd = config.get('password', None)
        region = config.get('region', 'eu')
        
        if not login or not passwd:
            logger.warning('No email or password in configuration file')
            return
        if region not in ['eu', 'ap', 'us']:
            logger.warning('Please select the right region: eu / ap / us')
            return

        base_url = "https://iotx-%s.meross.com" % region
        logger.info("Meross devices discovery")
        self.client = await MerossHttpClient.async_from_user_password(api_base_url=base_url, email=login, password=passwd)
        self.manager = MerossManager(http_client=self.client)
        # from meross_iot.manager import TransportMode
        # self.manager.default_transport_mode = TransportMode.LAN_HTTP_FIRST
        await self.manager.async_init()
        await self.discover()

    async def discover(self):
        # discovery
        try:
            await self.manager.async_device_discovery()
        except aiohttp.client_exceptions.ClientConnectorError as e:
            logger.error(e)

        meross_devices = self.manager.find_devices()
        #import pdb;pdb.set_trace()
        # config
        devices_config = self.cfg.get('devices',{})
        # devices
        uuids = [d.meross.uuid for d in self.devices]
        for m_dev in meross_devices:
            # skip devices already known
            if m_dev.uuid in uuids:
                continue
            # find a class to handle this device
            klass = bindings.find_class(m_dev)
            if not klass:
                logger.warn(f"No binding for {m_dev.type}")
                continue
            # search config
            conf = devices_config.get(m_dev.uuid,None)
            if not conf:
                logger.info(f"Found a new device {m_dev.type} {m_dev.uuid}")
                base_addr = tools.get_random_base_uuid()
                devices_config.update({m_dev.uuid:{'base_addr':base_addr}})
                devices_config.inline_comments[m_dev.uuid] = m_dev.type
            else:
                base_addr = tools.get_uuid(conf.get('base_addr',None))
            # create device
            dev = klass(m_dev,base_addr)
            # poll the current state
            await dev.meross.async_update()
            await dev.update()
            # register device
            self.devices.append(dev)
            self.engine.add_devices(dev.embs)

    async def refresh(self):
        for d in self.devices:
            await d.update()

    def _exit(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()

def setup(eng):
    GW(eng)
    return True
