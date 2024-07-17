import socketio
from . import xaal_core
from . import json
from xaal.lib import tools

socket = socketio.Server(async_mode='gevent',ping_interval=0.5,json=json,cors_allowed_origins='*',logger=False)

def setup(wsgi_app):
    global socket
    app = socketio.Middleware(socket, wsgi_app)
    return app

def remote_addr(sid):
    env = socket.environ[sid]
    return env['REMOTE_ADDR']

def broadcast(event,sio_msg):
    socket.emit(event,json.prepare_cbor(sio_msg))

@socket.on('send_request')
def send_xaal_request(sid,addr,action,body):
    xaal_core.send_request(tools.get_uuid(addr),action,body)

@socket.on('query_attributes')
def query_attributes(sid,addr):
    dev = xaal_core.get_device(addr)
    if dev:
        msg = { 'address': dev.address.get(),'attributes':json.prepare_cbor(dev.attributes)}
        socket.emit('event_attributeChanges',msg,room=sid)

@socket.on('refresh_attributes')
def refresh_attributes(sid,addrs):
    print("[%s] Refresh attributes" % remote_addr(sid))
    for addr in addrs:
        dev = xaal_core.get_device(addr)
        if dev:
            msg = { 'address': dev.address.get(),'attributes':json.prepare_cbor(dev.attributes)}
            socket.emit('event_attributeChanges',msg,room=sid)
        else:
            print("Unknow device: %s" % addr)

@socket.on('debug')
def debug(sid):
    import pdb;pdb.set_trace()

@socket.on('ping_from_client')
def ping(sid):
    """ used for the latency test only"""
    socket.emit('pong_from_server', room=sid)
