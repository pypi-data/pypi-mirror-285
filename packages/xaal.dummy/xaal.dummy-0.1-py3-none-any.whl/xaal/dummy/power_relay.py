
from xaal.lib import Device,Engine,tools
import sys
import logging

logger = logging.getLogger("lamp.py")

def main(addr):
    if addr == None:
        addr = tools.get_random_uuid()
    dev = Device("powerrelay.basic",addr)
    dev.product_id = 'Dummy Power Relay'
    dev.url = 'http://www.acme.org'
        
    # attributes
    power = dev.new_attribute('power')

    dev.dump()
    
    # methods 
    def on():
        power.value = True
        print("%s ON" % dev)
    
    def off():
        power.value = False
        print("%s OFF" %dev)
    
    dev.add_method('turn_on',on)
    dev.add_method('turn_off',off)

    eng = Engine()
    eng.add_device(dev)
    eng.run()


if __name__ =='__main__':
    try:
        addr = None
        if len(sys.argv) > 1:
            addr = tools.get_uuid(sys.argv[-1])
        main(addr)
    except KeyboardInterrupt:
        pass
