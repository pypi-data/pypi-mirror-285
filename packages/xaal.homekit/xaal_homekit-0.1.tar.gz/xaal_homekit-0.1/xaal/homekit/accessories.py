from xaal.schemas import devices
from xaal.lib import tools,Device
from xaal.schemas import devices

from aiohomekit.model import ServicesTypes,CharacteristicsTypes

import json
import logging


logger = logging.getLogger(__name__)


def find_service_class(name):
    #return  Service
    if name in ['accessory-information']:
        return Information
    if name in ['light']:
        return Light
    if name in ['lightbulb']:
        return Lamp
    if name in ['occupancy']:
        # right now occupancy seems to he used for switch without state
        # w/ no state, i'm unable to monitor the change state.
        return Service
    if name in ['motion']:
        return Motion
    if name in ['contact']:
        return Contact
    if name in ['humidity']:
        return Humidity
    if name in ['temperature']:
        return Temperature
    if name in ['battery']:
        return Battery
    return Service


class Accessory(object):
    def __init__(self,aid,services,base_addr,xaal_gw):
        self.aid = aid
        self.services = services
        self.base_addr = base_addr
        self.last_addr = base_addr
        self.gw = xaal_gw
        self.information = None
        self.subscribed = {}
        logger.info(f"Loading Accessory {aid}")
        self.setup()
      
    def setup(self):
        for k in self.services:
            s_type = k['type']
            s_iid  = k['iid']
            s_name = ServicesTypes.get_short(s_type)
            klass = find_service_class(s_name)
            logger.debug(f"Service: {s_iid} {s_name}")
            try:
                srv = klass(k,self)
            except Exception:
                import pdb;pdb.set_trace()
            if srv.__class__ == Service:
                logger.warn(f"Unknow service: {s_name}")
            if isinstance(srv,Information):
                self.information = srv
            for k in  srv.subscribed:
                self.subscribed.update({(self.aid,k):srv})

    def add_device(self,dev):
        dev.address = self.last_addr
        self.gw.engine.add_device(dev)
        self.last_addr = self.last_addr+1
        if self.information:
            dev.vendor_id  = self.information.vendor_id
            dev.product_id = self.information.product_id
            dev.version    = self.information.version
            dev.info       = self.information.info
            dev.hw_id      = self.information.hw_id
        return dev


def get_short_type(characteristic):
    tmp = characteristic.get("type",None)
    if tmp:
        return CharacteristicsTypes.get_short(tmp)
    return None

class Service(object):
    def __init__(self,service,accessory):
        self.service = service
        self.accessory = accessory
        self.characteristics = service.get('characteristics',[])
        self.subscribed = []
        self.dump()
        self.setup()
        
    def get_data(self,characteristic):
        c_iid  = characteristic.get('iid',None)
        c_type = get_short_type(characteristic)
        desc   = characteristic.get('description',None)
        value  = characteristic.get('value',None)
        unit   = characteristic.get('unit',None)
        return (c_iid,c_type,desc,value,unit)

    def search(self,c_type):
        for obj in self.characteristics:
            cur_c_type = get_short_type(obj)
            if c_type == cur_c_type:
                return  self.get_data(obj)
        return (None,None,None,None,None)

    def search_value(self,c_type):
        (c_iid,c_type,desc,value,unit) = self.search(c_type)
        return value

    def monitor(self,c_type):
        (c_iid,c_type,desc,value,unit) = self.search(c_type)
        if c_iid:
            self.subscribe(c_iid)
        return (c_iid,c_type,desc,value,unit)

    def dump(self):
        for obj in self.characteristics:
            (c_iid,c_type,desc,value,unit) = self.get_data(obj)
            if unit:
                print(f"  =>{c_iid} [{c_type}] {desc} : {value} {unit}")
            else:
                print(f"  =>{c_iid} [{c_type}] {desc} : {value}")

    def setup(self):
        self.dump()

    def subscribe(self,c_iid):
        self.subscribed.append(c_iid)

    def add_device(self,dev):
        return self.accessory.add_device(dev)

    def handler(self,src,data):
        print(f" {self} : {data}")

    def map_device(self,c_type,new_dev_func,attr_name,value_func):
        (c_iid,c_type,desc,value,unit) = self.monitor(c_type)
        dev = self.add_device(new_dev_func())
        if value!=None:
            dev.attributes[attr_name] = value_func(value)
        return dev

    def map_value(self,dev,data,attr_name,value_func):
        value = data.get('value',None)
        if value != None:
            dev.attributes[attr_name] = value_func(value)


# ===========================================================================
# Below, you will find the data mapping. We can reduce this code easily 
# but this should occur after more testing. I'm quite sure, we will find
# some buggy HK devices... and reducing before testing is a bad idea
# ===========================================================================
class Information(Service):
    def setup(self):
        #import pdb;pdb.set_trace()
        self.vendor_id  = 'HomeKit:' + self.search_value('manufacturer')
        self.product_id = self.search_value('model')
        self.version    = self.search_value('firmware.revision')
        self.info       = self.search_value('name')
        self.hw_id      = self.search_value('serial-number')

class Light(Service):
    def setup(self):
        self.dev = self.map_device('light-level.current',devices.luxmeter,'illuminance',int_func)
    def handler(self,src,data):
        self.map_value(self.dev,data,'illuminance',int_func)

class Lamp(Service):
    def setup(self):
        self.dev = self.map_device('on',devices.lamp,'light',bool_func)
        self.dev.methods['turn_on'] = self.debug

    def debug(self):
        import pdb;pdb.set_trace()

    def handler(self,src,data):
        self.map_value(self.dev,data,'light',bool_func)

class Motion(Service):
    def setup(self):
        self.dev = self.map_device('motion-detected',devices.motion,'presence',bool_func)
    def handler(self,src,data):
        self.map_value(self.dev,data,'presence',bool_func)

class Contact(Service):
    def setup(self):
        self.dev = self.map_device('contact-state',devices.contact,'detected',bool_func)
    def handler(self,src,data):
        self.map_value(self.dev,data,'detected',bool_func)

class Humidity(Service):
    def setup(self):
        self.dev = self.map_device('relative-humidity.current',devices.hygrometer,'humidity',round_2_func)
    def handler(self,src,data):
        self.map_value(self.dev,data,'humidity',round_2_func)

class Temperature(Service):
    def setup(self):
        self.dev = self.map_device('temperature.current',devices.thermometer,'temperature',round_2_func)
    def handler(self,src,data):
        self.map_value(self.dev,data,'temperature',round_2_func)
     
class Battery(Service):
    def setup(self):
        self.dev = self.map_device('battery-level',devices.battery,'level',int_func)
    def handler(self,src,data):
        self.map_value(self.dev,data,'level',int_func)


def int_func(value):
    return int(value)

def round_2_func(value):
    return round(value,2)

def bool_func(value):
    return bool(value)