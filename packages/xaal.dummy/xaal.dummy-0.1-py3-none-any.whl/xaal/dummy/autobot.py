
import time,random,sys
from xaal.lib import Engine,Device,tools
from xaal.schemas import devices

eng = None

def usage():
    print("Usage:")
    print("  %s target_address" % sys.argv[0])

def wait():
    # the plain old engine has to be looped to process the requests
    t0 = time.time()
    while time.time() < (t0+3):
        eng.loop()

def main():
    global eng
    target = tools.get_uuid(sys.argv[-1])
    if not target:
        usage()
        return

    dev = devices.hmi()
    dev.vendor_id = "RAMBo"
    dev.product_id = "Fake Auto Switcher"
    dev.info = 'Switcher for %s' % target
    dev.dump()

    eng = Engine()
    eng.add_device(dev)

    while 1:
        eng.send_request(dev,[target,],'turn_on')
        print(' => turn_on')
        wait()

        brightness = random.randint(0,100)
        eng.send_request(dev,[target,],'set_brightness',{'brightness':brightness})
        print(' => set_brightness %s' % brightness)
        wait()

        eng.send_request(dev,[target,],'turn_off')
        print(' => turn_off')
        wait()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Bye ..")