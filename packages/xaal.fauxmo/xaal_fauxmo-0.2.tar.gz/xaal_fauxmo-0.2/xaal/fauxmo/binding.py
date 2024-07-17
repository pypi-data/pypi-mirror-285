import logging
import asyncio
from fauxmo.plugins import FauxmoPlugin
from xaal.monitor import Monitor


import time
import asyncio

import nest_asyncio
nest_asyncio.apply()


logger = logging.getLogger()

monitor = None
on_off = ['off','on']

MAP = {
    'lamp':          ['turn_on','turn_off','light'],
    'powerrelay':    ['turn_on','turn_off','power'],
    'shutter':       ['down','up',None],
    'scenario':      ['run','abort',None],
}

def setup(device,filter_func):
    global monitor
    monitor = Monitor(device,filter_func)
    return monitor

def get_device(addr):
    return monitor.devices.get_with_addr(addr)


def send(addr,action,body=None):
    eng = monitor.engine
    eng.send_request(monitor.dev,[addr,],action,body)

class XAALPlugin(FauxmoPlugin):
    def setup(self,targets):
        self.targets = targets

    def get_devices(self):
        r = []
        for addr in self.targets:
            dev = get_device(addr)
            if dev:
                r.append(dev)
        return r

    def get_mapping(self,device):
        if device.dev_type == None:
            return None
        for k in MAP.keys():
            if device.dev_type.startswith(k):
                return MAP[k]
        logger.warning(f"Unable to find mapping for {device}")
        return None

    def on(self):
        for dev in self.get_devices():
            tmp = self.get_mapping(dev)
            if tmp == None: continue
            if tmp[0]:
                send(dev.address,tmp[0])
        return True

    def off(self):
        for dev in self.get_devices():
            tmp = self.get_mapping(dev)
            if tmp == None: continue
            if tmp[1]:
                send(dev.address,tmp[1])
        return True


    def get_state(self):
        # Alexa send a bunch (3) + (2) get_state request without any delay
        # Due to async use in Fauxmo, we need to async.sleep() to receive 
        # device update throught the monitor.. 
        # but the get_state is not async :( .. so no await or waitfor.. 
        # Only ensure_future() and run_until .. 
        # Last important notice : Python 3.9 avoid the run_until_complete
        # while loop is already running. nest-asyncio come to rescue !
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._get_state())
        return self.value

    async def _get_state(self):
        # we wait for 0.2 sec if the value isn't what we expected
        # this let's the device (and monitor) to push new value for 
        # the next call
        self.value = self.__get_state()
        if self.value != self._latest_action:
            logger.warning(f'state={self.value} != latest_action={self._latest_action}')
            await asyncio.sleep(0.2)

    def __get_state(self):
        "loops throught devices to find a least one w/ the right state"
        for dev in self.get_devices():
            tmp = self.get_mapping(dev)
            if tmp == None: continue
            if tmp[2]:
                value = dev.attributes.get(tmp[2],None)
                if value == None: continue
                if on_off[value] == self._latest_action:
                    return self._latest_action
            else:
                # fake state due to missing state for this device
                return self._latest_action

        # no device found with the right state, so send 
        # the wrong state instead. sending "unknown"
        # should be better, but it raise a big warning
        if self._latest_action == 'on':
            return 'off'
        return 'on'
    
