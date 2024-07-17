from xaal.schemas import devices 
from xaal.lib import helpers, tools
import sys


def main(engine):
    addr = None
    if len(sys.argv) > 1:
        addr = tools.get_uuid(sys.argv[-1])
        if not addr:
            print('Wrong address')
            sys.exit(1)

    dev = devices.lamp_toggle(addr)
    dev.vendor_id = 'RAMBo Team'
    dev.product_id = 'lamp_minimal'
    dev.info = 'Dummy Mini Lamp'
    dev.attributes['light'] = False

    # methods
    def on():
        dev.attributes['light'] = True

    def off():
        dev.attributes['light'] = False

    def toggle():
        dev.attributes['light'] = not dev.attributes['light']

    dev.methods['turn_on'] = on
    dev.methods['turn_off'] = off
    dev.methods['toggle'] = toggle
    dev.dump()

    engine.add_device(dev)
    return True


if __name__ =='__main__':
    helpers.run_async_package('lamp_minimal', main)
