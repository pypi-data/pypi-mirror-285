from xaal.lib import tools,Device,AsyncEngine
from xaal.schemas import devices


import asyncio
import socketio
import atexit
import logging


logging.getLogger('socketio.client').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)

PACKAGE_NAME = 'xaal.sensfloor'
logger = logging.getLogger(PACKAGE_NAME)


class GW(object):
    def __init__(self,engine):
        self.engine = engine
        self.devices = {}
        atexit.register(self._exit)
        self.config()
        self.setup()
        
    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['config']['url']='http://floor1.enstb.org:8000/'
            cfg['devices'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg

    def setup(self):
        # socketio config
        self.sio = socketio.AsyncClient(engineio_logger=True,ssl_verify=False)
        self.sio.on('alarms-detected',self.on_alarm)
        # xaal gateway 
        addr = tools.get_uuid(self.cfg['config']['addr'])
        self.gw = devices.gateway(addr)
        self.engine.add_device(self.gw)

        for k in self.cfg['devices']:
            cfg = self.cfg['devices'][k]
            dev = self.add_device(k,cfg['type'],tools.get_uuid(cfg['addr']))
            self.engine.add_device(dev)


    def add_device(self,idx,al_type,addr=None):
        if not addr:
            addr = tools.get_random_uuid()
        dev = None
        if al_type == 'fall':
            dev = devices.falldetector(addr)
        if al_type == 'presence':
            dev = devices.motion(addr)
        if dev==None:
            return 
        logger.debug(f"New device {addr} {idx}")
        dev.vendor_id = 'Future Shape'
        dev.product_id='SensFloor'
        dev.info='zone index: %s' % idx

        self.devices.update({idx:dev})
        self.engine.add_device(dev)
        return dev


    def get_device(self,idx,al_type):
        dev = self.devices.get(idx,None)
        return dev


    def on_alarm(self,data):
        active = []
        for k in data:
            #print(k)
            idx = str(k['index'])
            al_type = k['type']
            state = k['state']
            dev = self.get_device(idx,al_type)
            if dev == None:
                dev = self.add_device(idx,al_type)
                self.cfg['devices'][str(idx)] = {'addr':dev.address,'type':al_type}
            
            if dev.dev_type=='motion.basic':
                dev.attributes['presence'] = True
                active.append(dev)
        #print(active)
        for dev in self.devices.values():
            if dev in active:continue
            if dev.dev_type=='motion.basic':
                dev.attributes['presence'] = False            
        

    def _exit(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()

#    async def xaal_task(self):
#        await self.engine.run()

    async def sio_task(self):
        url = self.cfg['config']['url']
        await self.sio.connect(url)#transports='polling')
        await self.sio.wait()


def stop():
    import pdb;pdb.set_trace()


def setup(eng):
    gw = GW(eng)
    eng.on_stop(stop)
    eng.new_task(gw.sio_task())
    return True