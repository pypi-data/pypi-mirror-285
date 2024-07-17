from xaal.lib import Device,tools
from .cmdclass import COMMAND_CLASS

class ZDevice(object):
    
    def __init__(self,node,gateway):
        self.node = node
        self.gw = gateway
        self.devices = []
        self.values = {}
        self.config()
        self.setup()
        
    def config(self):
        """ read config files, search base_addr & group"""
        cfg = self.gw.cfg['products']
        key = str(self.node.node_id)
        if key in cfg.keys():
            tmp = cfg[key]['base_addr']
            self.base_addr =  tools.get_uuid(tmp)
        else:
            self.gw.save_config=True
            cfg.update({key:{}})
            cfg[key]['base_addr'] = str(tools.get_random_base_uuid())
            cfg[key]['group'] = str(tools.get_random_uuid())
        cfg.inline_comments[key] = self.node.product_name

    def new_device(self,devtype):
        """ embed an new device """
        node_id = str(self.node.node_id)
        cfg = self.gw.cfg['products'][node_id]
        dev = Device(devtype)
        dev.vendor_id  = "IHSEV/OpenZWave"
        dev.product_id = self.node.product_name
        dev.hw_id      = node_id
        dev.url        = "http://www.openzwave.com"
        dev.address    = tools.get_uuid(cfg['base_addr']) + len(self.devices) + 1
        dev.group_id   = tools.get_uuid(cfg['group'])
        dev.info       = '%s/%s' % (self.node.type,node_id)
        self.devices.append(dev)
        return dev

    def start(self):
        for k in self.values:
            self.handle_value_changed(self.values[k])
            self.values[k].refresh()
            
    def monitor_value(self,name,cmd_class,instance=1,idx=0):
        val = self.gw.get_value(self.node.node_id,cmd_class,instance,idx)
        if val:
            self.values[name] = val

    def set_value(self,name,val):
        self.values[name].data = val

    def get_value(self,name):
        return self.values[name]
        
    def dump(self):
        self.gw.dump_product(self.node.node_id)
    
    def setup(self):
        """ You should overide this for your product"""
        pass
    
    def handle_value_changed(self,value):
        """ You can overide this for your product"""
        pass
    
        
