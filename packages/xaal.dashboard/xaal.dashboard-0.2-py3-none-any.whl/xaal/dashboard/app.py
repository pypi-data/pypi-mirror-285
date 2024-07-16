from email.policy import default
from gevent import monkey; monkey.patch_all(thread=False)
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import gevent

from bottle import Bottle,debug,get,redirect,static_file,TEMPLATE_PATH,default_app

# load pages 
from . import pages
# load components
from .pages import warp10
from .core import xaal_core
from .core import sio 

import os

HOME = os.path.dirname(__file__)
PORT = 9090

server = None

@get('/static/<filename:path>')
def send_static(filename):
    root = os.path.join(HOME,'static')
    return static_file(filename, root=root)

@get('/')
def goto_home():
    redirect('/grid')
    
def run():
    """ start the xAAL stack & launch the HTTP stuff"""
    global server
    # add the default template directory to the bottle search path
    root = os.path.join(HOME,'templates')
    TEMPLATE_PATH.append(root)
    warp10.setup()
    # debug disable template cache & enable error reporting
    debug(True)
    #bottle_app = Bottle()
    #app = sio.setup(bottle_app)
    app = sio.setup(default_app())
    #server = WSGIServer(("", 9090), app, handler_class=WebSocketHandler, keyfile=KEY_PATH+'key.pem', certfile=KEY_PATH+'cert.pem')
    server = WSGIServer(f":{PORT}", app, handler_class=WebSocketHandler)
    server.serve_forever()

def stop():
    global server
    server.stop()

def main():
    # This apps can run with gevent alone (without asyncio)   
    # bottle.py use gevent to handle websocket. 
    # I maintain this to be able to run it on older 2.7 Python
    from xaal.lib import Engine
    engine = Engine()
    xaal_core.setup(engine)
    green_let = gevent.Greenlet(xaal_core.xaal_loop, engine)
    green_let.start()
    try:
        run()
    except KeyboardInterrupt:
        stop()
        print("Bye Bye...")

def setup(engine):
    # This is a AsyncEngine only setup, used w/ xaal-pkgrun for example
    xaal_core.setup(engine)
    gevent.spawn(run)
    engine.on_stop(stop)
    return True

if __name__ == '__main__':
    main()
