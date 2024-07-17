from gevent import monkey; monkey.patch_all(thread=False)

from xaal.lib import Engine,Device,helpers,tools
from bottle import Bottle,default_app,debug,get,request,response,redirect,static_file,template

from . import devices
import os
import platform
import logging

import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

PACKAGE_NAME = "xaal.fakeinput"
DEFAULT_PORT = 8081
HOME = os.path.dirname(__file__)
VIEWS = [os.path.join(HOME,"views"),]

logger = logging.getLogger(PACKAGE_NAME)
server = None
cfg = None
fake_devices = []
app = Bottle()

def setup_xaal(engine):
    """ setup xAAL Engine & Device. And start it in a Greenlet"""
    global cfg
    cfg = tools.load_cfg(PACKAGE_NAME)
    if not cfg:
        cfg = tools.new_cfg(PACKAGE_NAME)
        logger.info(f"No config file found, building a new one {cfg.filename}")
        cfg['config']['port'] = DEFAULT_PORT
        cfg['devices'] = random_devices()
        cfg.write()
    dev            = Device("hmi.basic")
    dev.address    = tools.get_uuid(cfg['config']['addr'])
    dev.vendor_id  = "IHSEV"
    dev.product_id = "Fake buttons, switches, contact"
    dev.version    = 0.1
    dev.info       = "%s@%s" % (PACKAGE_NAME,platform.node())

    engine.add_device(dev)
    load_config(engine)

def xaal_loop(engine):
    """ xAAL Engine Loop Greenlet"""
    engine.start()
    while 1:
        engine.loop()

def random_devices():
    tmp = {}
    for k in ['button','contact','switch','motion']:
        uid = str(tools.get_random_uuid())
        tmp[uid] = {'name':'fake %s' % k,'type':k}
    return tmp

def load_config(engine):
    cfg_devices = cfg.get('devices',[])
    for k in cfg_devices:
        addr = tools.get_uuid(k)
        type_ = cfg_devices[k].get('type',None)
        name =  cfg_devices[k].get('name',None)
        dev = None
        if type_ :
            if type_ == 'button':
                dev = devices.Button(addr,name,engine)
            if type_ == 'switch':
                dev = devices.Switch(addr,name,engine)
            if type_ == 'contact':
                dev = devices.Contact(addr,name,engine)
            if type_ == 'motion':
                dev = devices.Motion(addr,name,engine)

        if dev:
            fake_devices.append(dev)

def search_device(addr):
    uid = tools.str_to_uuid(addr)
    for k in fake_devices:
        if k.dev.address == uid:
            return k
    return None

@app.get('/static/<filename:path>')
def static(filename):
    root = os.path.join(HOME,'static')
    return static_file(filename, root=root)

@app.get('/')
def index():
    return template('index.tpl',template_lookup=VIEWS,request=request,devices=fake_devices) 

@app.get('/api/click/<addr>/<click_type:int>')
def click(addr,click_type):
    dev = search_device(addr)
    if dev and isinstance(dev,devices.Button):
        dev.click(click_type)

@app.get('/api/set_on/<addr>')
def set_on(addr):
    dev = search_device(addr)
    if dev and not isinstance(dev,devices.Button):
        dev.set_on()

@app.get('/api/set_off/<addr>')
def set_off(addr):
    dev = search_device(addr)
    if dev and not isinstance(dev,devices.Button):
        dev.set_off()

def run():
    """ start the xAAL stack & launch the HTTP stuff"""
    global server
    helpers.set_console_title(PACKAGE_NAME)
    helpers.setup_console_logger(level=logging.INFO)
    debug(True)
    port = int(cfg.get('config').get('port',DEFAULT_PORT))
    logger.info("HTTP Server running on port : %d" % port)
    server = WSGIServer(f":{port}", app, handler_class=WebSocketHandler)
    server.serve_forever()

def stop():
    server.stop()

def main():
    # This apps can run with gevent alone (without asyncio)   
    # bottle.py use gevent to handle websocket. 
    # I maintain this to be able to run it on older 2.7 Python
    engine = Engine()
    setup_xaal(engine)
    green_let = gevent.Greenlet(xaal_loop, engine)
    green_let.start()
    try:
        run()
    except KeyboardInterrupt:
        stop()
        print("Bye Bye...")

def setup(engine):
    # This is a AsyncEngine only setup, used w/ xaal-pkgrun for example
    setup_xaal(engine)
    gevent.spawn(run)
    engine.on_stop(stop)
    return True
    
if __name__ == '__main__':
    main()
