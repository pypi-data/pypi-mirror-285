
from xaal.lib import Engine,Device,tools
import platform
import copy
import atexit
import logging

PACKAGE_NAME = "xaal.metadb"
logger = logging.getLogger(PACKAGE_NAME)


class MetaDB(object):
    def __init__(self,engine):
        self.engine = engine
        self.config()
        self.setup()
        self.dirty = False
        atexit.register(self.periodic_save)

    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            logger.info('Missing config file, building a new one')
            cfg = tools.new_cfg(PACKAGE_NAME)
            cfg['devices'] = {}
            cfg.write()
        self.cfg = cfg

    def setup(self):
        addr = tools.get_uuid(self.cfg['config']['addr'])
        dev            = Device("metadatadb.basic")
        dev.address    = addr
        dev.vendor_id  = "IHSEV"
        dev.product_id = "Metadata database"
        dev.version    = 0.1
        dev.info       = "%s@%s" % (PACKAGE_NAME,platform.node())
        
        dev.add_method('get_devices',self.get_devices)
        dev.add_method('get_keys_values',self.get_keys_values)
        dev.add_method('get_value', self.get_value)
        dev.add_method('update_keys_values', self.update_keys_values)
        
        self.dev = dev
        self.engine.add_device(dev)
        self.engine.add_timer(self.periodic_save,60)

    def get_devices(self,_key=None,_value=None):
        devices = self.cfg['devices'] 
        result = devices.keys()
        logger.debug("Searching for %s / %s" % (_key,_value))

        # search for a given key=value and break
        if _key and _value:
            value = str(_value)
            temp = [] 
            for dev in result:
                if _key in devices[dev].keys():
                    if devices[dev][_key] == value:
                        temp.append(dev)
            return {'key':_key,'value' : _value, 'devices' : temp}
        
        # filter key
        if _key:
            for dev in copy.copy(result):
                #print("%s %s %s" % (dev,key,devices[dev].keys()))
                if _key not in devices[dev].keys():
                    result.remove(dev)

        # filter value
        if _value:
            value = str(_value)
            for dev in copy.copy(result):
                print("%s %s %s" % (dev,value,devices[dev].values()))
                if value not in devices[dev].values():
                    result.remove(dev)
        return {'key':_key,'value' : _value, 'devices' : result}

    def get_device(self,addr):
        devices = self.cfg['devices']
        try:
            return devices[str(addr)]
        except KeyError:
            return None

    def get_keys_values(self,_device):
        dev = self.get_device(_device)
        if dev:
            return {'device':_device,'map' : dev.dict()}
        # logger.debug('Unknown device %s' % _device)
        return {'device':_device,'map' : {}}

    def get_value(self,_device,_key):
        dev = self.get_device(_device)
        if not dev:
            logger.info('Unknown device %s' % _device)
            return 
        try:
            return {'device': _device, 'key':_key,'value':dev[_key]}
        except KeyError:
            logger.info('Unknown key %s for %s' % (_key,_device))
            pass

    def update_keys_values(self,_device,_map):
        dev = self.get_device(_device)
        updated = {}

        if dev:
            # if _map is empty, remove the device
            if _map == None:
                # self.cfg['devices'].pop(str(_device))
                dev = {}
                self.dirty = True
                return
            # loop throught the map 
            for k in _map:
                updated.update({k:_map[k]})
                self.dirty = True
                # remove item if empty
                if _map[k] == None:
                    dev.pop(k)
                else:
                    dev.update({k:_map[k]})
                
        elif _map != None:
            updated = {}
            for k, v in _map.items():
                if v != None:
                   updated.update({k:v})
            self.cfg['devices'][str(_device)]=updated
            self.dirty = True

        if self.get_device(_device) == {}:
            self.cfg['devices'].pop(str(_device))

        if len(updated):
            body = {'device':_device,'map':updated}
            self.engine.send_notification(self.dev,'keys_values_changed',body)
            logger.debug(f"Updated {_device} => {self.get_device(_device)}")
            
    def periodic_save(self):
        if self.dirty:
            devices = copy.copy(self.cfg['devices'])
            #for key,val in devices.items():
            #    if val == None:
            #        devices.pop(key)
            devices = {key: val for key, val in sorted(devices.items(), key = lambda ele: ele[0])}
            self.cfg['devices'] = devices
            logger.info("Saving configuration file")
            self.cfg.write()
            self.dirty = False

def setup(eng):
    MetaDB(eng)
    return True

