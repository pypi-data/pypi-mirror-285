
import asyncio
from asyncio.events import get_event_loop
import logging
import signal
import sys
from functools import partial

from fauxmo import __version__
from fauxmo.plugins import FauxmoPlugin
from fauxmo.protocols import Fauxmo, SSDPServer
from fauxmo.utils import get_local_ip, make_udp_sock


import coloredlogs
coloredlogs.install(10)
import logging

PACKAGE_NAME = 'xaal.fauxmo'
logger = logging.getLogger(PACKAGE_NAME)
logging.getLogger('fauxmo').setLevel(logging.DEBUG)
logging.getLogger('asyncio').setLevel(logging.DEBUG)

class FakeLamp(FauxmoPlugin):
    def on(self):
        print("On")
        return True
    
    def off(self):
        print("Off")
        return True

    def get_state(self):
        return self.latest_action


def main():
    logger.info(f"Fauxmo {__version__}")

    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    asyncio.set_event_loop(loop)

    fauxmo_ip = get_local_ip()
    # SSDP server 
    ssdp_server = SSDPServer()
    # HTTP servers to handler /upnp/control/.. 
    servers = []


    port = 30000
    for k in ["lampe bureau","lampe salon","lampe salle"]:

        port = port + 1
        plugin = FakeLamp(name=k,port=port)

        fauxmo = partial(Fauxmo, name=plugin.name, plugin=plugin)
        coro = loop.create_server(fauxmo, host=fauxmo_ip, port=port)
        server = loop.run_until_complete(coro)
        server.fauxmoplugin = plugin
        servers.append(server)

        ssdp_server.add_device(plugin.name, fauxmo_ip, plugin.port)
        logger.debug(f"Started fauxmo device: {repr(fauxmo.keywords)}")


    logger.info("Starting UDP server")
    listen = loop.create_datagram_endpoint(
        lambda: ssdp_server, sock=make_udp_sock()
    )
    transport, _ = loop.run_until_complete(listen)

    for signame in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, signame), loop.stop)

    loop.run_forever()

    # Will not reach this part unless SIGINT or SIGTERM triggers `loop.stop()`
    logger.debug("Shutdown starting...")
    transport.close()
    for idx, server in enumerate(servers):
        logger.debug(f"Shutting down server {idx}...")
        server.fauxmoplugin.close()
        server.close()
        loop.run_until_complete(server.wait_closed())

    loop.close()

if __name__ == '__main__':
    main()
