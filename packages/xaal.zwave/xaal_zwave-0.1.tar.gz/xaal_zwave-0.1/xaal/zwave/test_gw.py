
import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from pydispatch import dispatcher
import sys
import time

from .cmdclass import COMMAND_CLASS
#import auto

device="/dev/zwave"
network = None

def connected():
    print("Connecting..")

def ready():
    print("Ready")

def disconnected():
    print("Disconnected")

def node_update(network, node):
    print('signal : Node update : {}.'.format(node))

def value_update(network, node, value):
    print('signal : Value update : {}.'.format(value))


def dump_device(node_id):
    zdev = network.nodes[node_id]
    print("***** %s" % zdev.product_name)
    print("***** %s:%s:%s" % (zdev.manufacturer_id,zdev.product_id,zdev.product_type))
    for k in zdev.values:
        val = zdev.values[k]
        klass = None
        if val.command_class !=None:
            klass = COMMAND_CLASS(val.command_class)
        print("%s/%s/%s [%s] %s%s %s" % (k,val.instance,val.index,val.label,val.data,val.units,klass))


def get_value(node_id,cmd_class,instance=1,idx=0):
    zdev = network.nodes[node_id]
    for k in zdev.values:
        val = zdev.values[k]
        if ((cmd_class == COMMAND_CLASS(val.command_class)) and (val.index==idx) and (val.instance == instance)):
            return val
    return None


options = ZWaveOption(device)
options.set_console_output(False)
options.lock()

network = ZWaveNetwork(options, autostart=False)
network.start()

dispatcher.connect(connected, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
dispatcher.connect(disconnected, ZWaveNetwork.SIGNAL_NETWORK_FAILED)
dispatcher.connect(ready, ZWaveNetwork.SIGNAL_NETWORK_READY)
dispatcher.connect(node_update, ZWaveNetwork.SIGNAL_NODE)



for i in range(0,90):
    if network.is_ready:
        print("***** Network is ready")
        dispatcher.connect(value_update, ZWaveNetwork.SIGNAL_VALUE)
        break
    else:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1.0)

#dump_device(2)


#zdev = network.nodes[10]
#values = zdev.values

import pdb;pdb.set_trace()



