
from xaal.lib import tools,Engine,Device,helpers
from xaal.monitor import Monitor

import platform
import logging

PACKAGE_NAME = "xaal.monitorexample"

logger = logging.getLogger(PACKAGE_NAME)

def display_event(event,dev):
    logger.debug("MonitorExample: %s %s %s" %(event, dev.address, dev.attributes))

def monitor_example(engine):
    # load config
    cfg = tools.load_cfg_or_die(PACKAGE_NAME)
    # create a device & register it
    dev            = Device("hmi.basic")
    dev.address    = tools.get_uuid(cfg['config']['addr']) or tools.get_random_uuid()
    dev.vendor_id  = "IHSEV"
    dev.product_id = "Monitor Example"
    dev.version    = 0.1
    dev.info       = "%s@%s" % (PACKAGE_NAME,platform.node())
    engine.add_device(dev)

    db_server = None
    if 'db_server' in cfg['config']:
        db_server = tools.get_uuid(cfg['config']['db_server'])
    else:
        logger.info('You can set "db_server" in the config file')
    # start the monitoring
    mon = Monitor(dev,db_server=db_server)
    mon.subscribe(display_event)
    return mon

def run():
    print("Monitor test")
    helpers.setup_console_logger()
    eng = Engine()
    mon = monitor_example(eng)
    try:
        eng.run()
    except KeyboardInterrupt:
        import pdb;pdb.set_trace()

if __name__ == '__main__':
    run()
    
