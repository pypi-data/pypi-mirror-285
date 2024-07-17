xaal.monitor
============
This package is a library for monitoring the xAAL devices on the network. It provides a easy way to get the list of devices and their status
(attributes, description, metadata, etc...). It also provides a simple way to subscribe to events.

This package is used by a lot of xAAL programs like: The dashboard, the REST API, the Home Assistant plugin...

Usage
-----
.. code:: python

    from xaal.monitor import Monitor
    from xaal.schemas import devices
    from xaal.lib import Engine

    def on_event(ev_type, device):
        print("Event type: %s from device %s" % (ev_type, device))

    dev = devices.hmi()
    eng = Engine()
    eng.add_device(dev)
    mon = Monitor(dev)
    mon.subscribe(on_event)
    eng.run()
