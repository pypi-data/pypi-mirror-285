from xaal.lib import tools
from xaal.schemas import devices

from . import binding

import atexit
import logging
import functools
import asyncio
import platform

from fauxmo.protocols import Fauxmo, SSDPServer
from fauxmo.utils import get_local_ip, make_udp_sock

PACKAGE_NAME = 'xaal.fauxmo'
logger = logging.getLogger(PACKAGE_NAME)

logging.getLogger('fauxmo').setLevel(logging.INFO)


class GW(object):
    def __init__(self,engine):
        self.engine = engine
        self.addrs = []
        self.config()
        self.setup_xaal()
        self.setup()

    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['devices'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg

    def setup_xaal(self):
        addr = tools.get_uuid(self.cfg['config'].get('addr',tools.get_random_uuid()))
        gw = devices.gateway(addr)

        gw.vendor_id  = 'IHSEV'
        gw.product_id = 'FauxMo Gateway'
        gw.info       = "%s@%s" % (PACKAGE_NAME,platform.node())
        self.engine.add_device(gw)
        self.gw = gw
        binding.setup(gw,self.filter)

    def filter(self,msg):
        if msg.source in self.addrs:
            return True
        return False

    def setup(self):
        self.ssdp_server = SSDPServer()
        self.fauxmo_ip = get_local_ip()
        loop = asyncio.get_event_loop()

        devices_cfg = self.cfg.get('devices',[])
        for k in devices_cfg:
            targets = [tools.get_uuid(addr) for addr in devices_cfg[k].get('targets',[])]
            self.addrs = self.addrs + targets
            port  = devices_cfg[k].get('port',None)
            plugin = binding.XAALPlugin(name=k,port=port)
            plugin.setup(targets)
            logger.info(f"Loaded {k}: {targets}")
            
            fauxmo = functools.partial(Fauxmo, name=plugin.name, plugin=plugin)
            coro = loop.create_server(fauxmo, host=self.fauxmo_ip, port=port)
            server = loop.run_until_complete(coro)
            server.fauxmoplugin = plugin

            self.ssdp_server.add_device(plugin.name, self.fauxmo_ip, plugin.port)
            logger.debug(f"Started fauxmo device: {repr(fauxmo.keywords)}")

        logger.info("Starting UDP server")
        listen = loop.create_datagram_endpoint(lambda: self.ssdp_server, sock=make_udp_sock())
        loop.run_until_complete(listen)


def setup(eng):
    GW(eng)
    return True
