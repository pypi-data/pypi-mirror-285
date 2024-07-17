
from xaal.lib import Device,Engine,tools
import sys

def main(addr):
    if addr == None:
        addr = tools.get_random_uuid()
    dev = Device("lamp.dimmer",addr)
    dev.product_id = 'Dummy Dimming Lamp'
    dev.url = 'http://www.acme.org'
    dev.info = 'Dummy Lamp7'

    # attributes
    light = dev.new_attribute('light',False)
    dimmer = dev.new_attribute('dimmer',50)
        
    # methods 
    def on():
        light.value = True
        print("%s ON" % dev)
    
    def off():
        light.value = False
        print("%s OFF" %dev)
    
    def dim(_brightness,_smooth=None):
        # this device doesn't support _smooth parameter
        val = int(_brightness)
        if (val <= 100) and (val >=0):
            dimmer.value = val
            print("%s Dimming to %d" % (dev,val))

    dev.add_method('turn_on',on)
    dev.add_method('turn_off',off)
    dev.add_method('set_brightness',dim)
    # this is a simple dimmer w/ no white color settings.
    dev.unsupported_methods = ['set_color_temperature']
    dev.unsupported_attributes = ['color_temperature']
    dev.dump()

    eng = Engine()
    eng.add_device(dev)
    eng.run()

if __name__ =='__main__':
    try:
        addr = None
        if len(sys.argv) > 1:
            addr = tools.get_uuid(sys.argv[-1])
            if not addr:
                print("Wrong address")
        main(addr)
    except KeyboardInterrupt:
        pass
