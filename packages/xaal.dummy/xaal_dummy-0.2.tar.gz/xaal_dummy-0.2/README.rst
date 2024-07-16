xaal.dummy
==========
This package provides some dummy (fake) devices for the xAAL Project. It is intended to be used for testing purposes.

Usage
-----
Run the module to see the available devices and how to run them.

  .. code:: bash

    python -m xaal.dummy
    ================= xAAL dummy devices =================

    This package contains some fake lamps, power_relay, and bots:
        - lamp:         a simple lamp implementation
        - lamp_minimal: a simple lamp using schema devices
        - power_relay:  a power relay
        - temperature:  a fake temperature sensor
        - autobot:      a bot than send turn_on/off and  set_brightness
        - asyncbot:     same as autobot with asyncio


    To run a module simply call: python -m xaal.dummy.module
    Example: python -m xaal.dummy.lamp 8e1495cc-b98b-11eb-8432-d6bd5fe18736

    All modules accept their address (uuid) as argument. Autobot uuid is the
    lamp's address to switch.

Here a simple example to run a lamp:

  .. code:: bash

    python -m xaal.dummy.lamp 8e1495cc-b98b-11eb-8432-d6bd5fe18736
