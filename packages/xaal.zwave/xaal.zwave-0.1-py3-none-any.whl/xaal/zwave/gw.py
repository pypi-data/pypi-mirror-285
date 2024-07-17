import platform
import sys,time
import logging

# Zwave imports
from openzwave.option import ZWaveOption
from openzwave.network import ZWaveNetwork
from openzwave.object import ZWaveException
from pydispatch import dispatcher

from xaal.lib import tools,Device
from . import cmdclass
from . import products

from prettytable import PrettyTable
import atexit

PACKAGE_NAME = "xaal.zwave"
logger = logging.getLogger(PACKAGE_NAME)

logging.getLogger("libopenzwave").setLevel(logging.INFO)
logging.getLogger("openzwave").setLevel(logging.INFO)

class GW(object):
    
    def __init__(self,engine):
        self.products = []
        self.engine = engine
        self.config()
        atexit.register(self._exit)
        self.setup_gw()
        self.setup_network()
        self.setup_products()

    def config(self):
        self.save_config = False
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            logger.info('Missing config file, building a new one')
            cfg = tools.new_cfg(PACKAGE_NAME)
            cfg['config']['port'] = '/dev/zwave'
            cfg['products'] = {}
            cfg.write()
        self.cfg = cfg
        
    def update_value(self,network,node,value):
        dev = self.get_product(node.node_id)
        if dev:
            dev.handle_value_changed(value=value)
        else:
            #print('update_value: {}.'.format(value))
            pass
            
    def update_node(self,network,node):
        if self.get_product(node.node_id) != None: return
        if node.is_ready:
            logger.info("new zwave device [%d]: %s" % (node.node_id,node.product_name))
            dev = self.add_product(node.node_id)
        
    def setup_network(self):
        cfg = self.cfg['config']
        options = ZWaveOption(cfg['port'])
        options.set_console_output(False)
        # comments the following lines if you want a log file.
        options.set_save_log_level('None')
        options.set_log_file("/dev/null")
        options.lock()
        self.network = ZWaveNetwork(options, autostart=False)
        dispatcher.connect(self.update_node,ZWaveNetwork.SIGNAL_NODE)    
        dispatcher.connect(self.update_value,ZWaveNetwork.SIGNAL_VALUE)
        # searching for device w/ wait loop is mandatory. If you don't do that
        # the openzwave lib will segfault.
        self.network.start()
        logger.info('searching for Zwave devices, this may take a while')
        for i in range(0,60):
            if self.network.is_ready:
                logger.info('Zwave network ready')
                break
            else:
                time.sleep(1.0)
                print("\rLoading [%d] " % i,end='')
                
    def setup_products(self):
        for k in self.network.nodes:
            node = self.network.nodes[k]
            if self.get_product(node.node_id):
                continue
            if (node and node.is_ready):
                self.add_product(k)

    def get_product(self,node_id):
        for dev in self.products:
            if dev.node.node_id == node_id:
                return dev

    def add_product(self,node_id):
        node = self.network.nodes[node_id]
        sig = "%s:%s:%s" % (node.manufacturer_id,node.product_id,node.product_type)
        klass=products.search(sig)
        if klass:
            dev = klass(node,self)
            self.products.append(dev)
            self.engine.add_devices(dev.devices)
            self.update_embedded()
            dev.start()
        else:
            logger.info('Unknow device %s %s' % (node.product_name,sig))
        
    def setup_gw(self):
        # last step build the GW device
        gw            = Device("gateway.basic")
        gw.address    = tools.get_uuid(self.cfg['config']['addr'])
        gw.vendor_id  = "IHSEV"
        gw.product_id = "OpenZwave gateway"
        gw.version    = 0.1
        gw.url        = "http://www.openzwave.com/"
        gw.info       = "%s@%s" % (PACKAGE_NAME,platform.node())
        emb = gw.new_attribute('embedded',[])
        self.engine.add_device(gw)
        self.gw = gw
        
    def update_embedded(self):
        result = [] 
        for prod in self.products:
            for dev in prod.devices:
                result.append(dev.address)
        emb = self.gw.get_attribute('embedded')
        emb.value = result
        
    def get_value(self,node_id,cmd_class,instance=1,idx=0):
        node = self.network.nodes[node_id]
        for k in node.values:
            val = node.values[k]
            # some devices have broken command_class
            if val.command_class == None: continue
            if ((cmd_class == cmdclass.COMMAND_CLASS(val.command_class)) and (val.index==idx) and (val.instance == instance)):
                return val
        return None

    def _exit(self):
        if self.save_config:
            logger.info('Saving configuration file')
            self.cfg.write()
    
    def dump_product(self,node_id):
        """ dumb method that display a zwave device"""
        zdev = self.network.nodes[node_id]
        print("***** %s" % zdev.product_name)
        print("***** %s:%s:%s" % (zdev.manufacturer_id,zdev.product_id,zdev.product_type))
        table = PrettyTable(["value","inst","idx","Label","Data","Units","Command class"])
        table.align["Label"] = 'l'
        table.align["Data"] = 'l'
        table.align["Command class"] = 'l'
        for k in zdev.values:
            val = zdev.values[k]
            if val.command_class:
                klass = cmdclass.COMMAND_CLASS(val.command_class)
            else:
                klass = 'Error'
            table.add_row([k,val.instance,val.index,val.label,val.data,val.units,klass])
        print(table)
        
        
def setup(eng):
    try:
        gw=GW(eng)
        return True
    except ZWaveException as err:
        logger.warning('Error w/ Zwave network: %s' % err.value)
