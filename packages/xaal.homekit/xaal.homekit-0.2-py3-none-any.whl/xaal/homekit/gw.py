from xaal.lib.asyncio import Engine
from xaal.lib import tools,Device,helpers

from aiohomekit import Controller

import atexit
import logging
import asyncio


from . import accessories

PACKAGE_NAME = 'xaal.homekit'
logger = logging.getLogger(PACKAGE_NAME)


# default aiohomekit pairing file aiohomekit.__main__
import pathlib
XDG_DATA_HOME = pathlib.Path.home() / ".local" / "share"
DEFAULT_PAIRING_FILE = XDG_DATA_HOME / "aiohomekit" / "pairing.json"


class GW(object):
    def __init__(self,engine):
        self.engine = engine
        self.accessories = []
        atexit.register(self._exit)
        self.config()
        
    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['devices'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg


    async def setup(self):
        self.controller = Controller()
        logger.info(f"Loading pairing file: {DEFAULT_PAIRING_FILE}")
        self.controller.load_data(DEFAULT_PAIRING_FILE)
        pairings = self.controller.pairings
        for k in pairings:
            logger.info(f"Loading pairing: {k}")
            pair = pairings[k]
            pair.dispatcher_connect(self.handler)
            await self.add_accessories(pair)
    
    async def add_accessories(self,pairing):
        accs = await pairing.list_accessories_and_characteristics()
        tmp = []
        for k in accs:
            aid = k['aid']
            cfg = self.cfg.get('devices',{}).get('%s'%aid,{})
            addr = None
            if cfg:
                uuid = cfg.get('base_addr',None)
                if uuid: addr=tools.get_uuid(uuid)
            if addr == None:
                addr = tools.get_random_base_uuid()
                self.cfg['devices'].update({'%s' % aid:{'base_addr':addr}})
            obj = accessories.Accessory(aid,k['services'],addr,self)
            self.accessories.append(obj)
            tmp = tmp + list(obj.subscribed.keys())
        await self.subscribe(pairing,tmp)

    async def subscribe(self,pairing,characteristics):
        logger.warn(characteristics)
        await pairing.subscribe(characteristics)
    
    def find_service(self,src):
        for acc in self.accessories:
            if src in acc.subscribed.keys():
                return acc.subscribed[src]
        return None
        

    def handler(self,data):
        for src in data:
            srv = self.find_service(src)
            if srv:
                srv.handler(src,data[src])
        

    def _exit(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()

def setup(eng):
    logger.info('Starting %s' % PACKAGE_NAME)
    gw = GW(eng)
    return True

def run():
    helpers.setup_console_logger()
    eng = Engine()
    gw = GW(eng)
    tasks = [ asyncio.ensure_future(eng.run()),
              asyncio.ensure_future(gw.setup()),  ]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

def main():
    try:
        run()
    except KeyboardInterrupt:
        print("Bye Bye")    

