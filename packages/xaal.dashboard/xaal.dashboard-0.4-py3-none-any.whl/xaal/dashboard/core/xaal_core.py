from xaal.lib import tools,Engine,Device,helpers
from xaal.monitor import Monitor
from . import sio

import platform
import gevent

import time
import logging

PACKAGE_NAME = "xaal.dashboard"
logger = logging.getLogger(PACKAGE_NAME)

# we use this global variable to share data with greenlet
monitor = None
config = {}

# used for uptime
started = time.time()

def monitor_filter(msg):
    """ Filter incomming messages. Return False if you don't want to use this device"""
    if msg.dev_type.startswith('cli.'):
        return False
    return True

def event_handler(ev_type,dev):
    logger.debug("Event %s %s" % (ev_type,dev.address))
    msg = { 'address': dev.address.get(),'attributes':dev.attributes}
    # FIXME: This should be in core.sio
    sio.broadcast('event_attributeChanges',msg)
    
def setup(engine):
    """ setup xAAL Engine & Device. And start it in a Greenlet"""
    global monitor,config
    helpers.setup_console_logger()
    cfg = tools.load_cfg(PACKAGE_NAME)
    if not cfg:
        logger.info('Missing config file, building a new one')
        cfg = tools.new_cfg(PACKAGE_NAME)
        cfg.write()
    dev            = Device("hmi.dashboard")
    dev.address    = tools.get_uuid(cfg['config']['addr'])
    dev.vendor_id  = "IHSEV"
    dev.product_id = "WEB Interface"
    dev.version    = 0.1
    dev.info       = "%s@%s" % (PACKAGE_NAME,platform.node())

    engine.add_device(dev)
    db_server = None
    if 'db_server' in cfg['config']:
        db_server = cfg['config']['db_server']
    else:
        logger.info('You can set "db_server" in the config file')
    monitor = Monitor(dev,filter_func=monitor_filter,db_server=tools.get_uuid(db_server))
    monitor.subscribe(event_handler)
    config = cfg

def xaal_loop(engine):
    """ xAAL Engine Loop Greenlet"""
    engine.start()
    while 1:
        engine.loop()

def send_request(addr,action,body):
    eng = monitor.dev.engine
    eng.send_request(monitor.dev,[addr],action,body)       

def get_uptime():
    return int(time.time() - started)

def get_device(addr):
    uuid = tools.get_uuid(addr)
    return monitor.devices.get_with_addr(uuid)

def update_kv(addr,kv):
    dev = get_device(addr)
    db_server = monitor.db_server
    if dev:
        body = {'device':dev.address,'map':kv}
        print(body)
        send_request(db_server,'update_keys_values',body)
        dev.set_db(kv)