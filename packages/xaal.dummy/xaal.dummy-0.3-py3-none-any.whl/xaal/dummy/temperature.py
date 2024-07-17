
from xaal.lib import Device,Engine,tools


import select
import sys
import tty
import termios
import logging


logger = logging.getLogger("temperature.py")


def keyboard_read():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        data = sys.stdin.read(1) 
        return data
    
def display_value(value):
    sys.stdout.write('\r Temp : %0.1f' % value)
    sys.stdout.flush()

            
def main(addr):
    if addr == None:
        addr = tools.get_random_uuid()
    dev = Device("thermometer.basic",addr)
    dev.product_id = 'Fake Thermometer'
    dev.url = 'http://www.acme.org'
        
    # attributes
    temp = dev.new_attribute('temperature')
    temp.value = 20.0

    print("Press +/- to change the temperature, q to quit")
    display_value(temp.value)
    
    def run():
        ch = keyboard_read()
        if ch:
            if ch == '+': temp.value = temp.value + 0.1
            if ch == '-': temp.value = temp.value - 0.1
            if ch == 'q' : sys.exit(0)
            display_value(temp.value)

    eng = Engine()
    eng.add_device(dev)
    eng.add_timer(run,0)
    eng.run()

if __name__ == '__main__':
    # drop blocking tty 
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        addr = None
        if len(sys.argv) > 1:
            addr = tools.str_to_uuid(sys.argv[-1])
            if not addr:
                print("Wrong address")
        main(addr)
    except KeyboardInterrupt:
        pass
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
