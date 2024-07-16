from xaal.lib import AsyncEngine,Device,tools
from xaal.schemas import devices
import functools

import random,sys,asyncio


def usage():
    print("Usage:")
    print("  %s target_address" % sys.argv[0])


def main():
    target = tools.get_uuid(sys.argv[-1])
    if not target:
        usage()
        return

    dev = devices.hmi()
    dev.vendor_id = "RAMBo"
    dev.product_id = "Async Auto Switcher"
    dev.info = 'Switcher for %s' % target
    dev.dump()

    eng = AsyncEngine()
    eng.add_device(dev)

    async def run():
        while 1:
            print(' => turn_on')
            eng.send_request(dev,[target,],'turn_on')
            await asyncio.sleep(5)

            print(' => turn_off')
            eng.send_request(dev,[target,],'turn_off')
            await asyncio.sleep(5)

            brightness = random.randint(0,100)
            print(' => set_brightness %i' % brightness)
            eng.send_request(dev,[target,],'set_brightness',{'brightness': brightness})
            await asyncio.sleep(5)

    eng.on_start(run)
    eng.on_stop(functools.partial(print,"Bye Bye"))
    eng.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Bye ..")
