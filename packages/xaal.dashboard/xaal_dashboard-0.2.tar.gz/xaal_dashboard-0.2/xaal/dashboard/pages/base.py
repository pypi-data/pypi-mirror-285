from .default import view,route,xaal_core

from bottle import request,response,redirect,get,post

import copy

@route('/stats')
@view('stats')
def stats():
    total = 0
    results = {}
    for dev in xaal_core.monitor.devices:
        total = total + 1
        try:
            k = dev.dev_type
            results[k]=results[k]+1
        except KeyError:
            results.update({k:1})
    r = {"title" : "Network stats"}
    r.update({"total"   :total})
    r.update({"dev_types":results})
    r.update({"uptime"  : xaal_core.get_uptime()})
    return r


@route('/bottle')
@view('bottle')
def info():
    r = {"title" : "Bottle Server Info"}
    r.update({"headers" : request.headers})
    r.update({"query"   : request.query})
    r.update({"environ" : copy.copy(request.environ)})
    return r



@route('/devices')
@view('devices')
def get_devices():
    r = {"title" : "devices list","active_menu":"devices"}
    devs = xaal_core.monitor.devices
    r.update({"devs" : devs})
    return r


@route('/generic/<addr>')
@view('generic')
def get_device(addr):
    r = {"title" : "device %s" % addr}
    dev = xaal_core.get_device(addr)
    if dev:
        r.update({"dev" : dev})
    return r

@get('/edit_metadata/<addr>')
@view('edit_metadata')
def edit_metadata(addr):
    r = {"title" : "device %s" % addr}
    dev = xaal_core.get_device(addr)
    if dev:
        r.update({"dev" : dev})
    return r


@post('/edit_metadata/<addr>')
@view('edit_metadata')
def save_metadata(addr):
    form = dict(request.forms.decode()) # just to shut up lint
    kv = {}
    for k in form:
        key = str(k)
        if form[k]=='': continue
        if key.startswith('key_'):
            id_ = key.split('key_')[-1]
            v_key = 'value_'+id_
            if v_key in form:
                if form[v_key] =='':
                    value = None
                else:
                    value = form[v_key]
                kv.update({form[k]:value})
    xaal_core.update_kv(addr,kv)
    return edit_metadata(addr)
    



@route('/grid')
@view('grid')
def test_grid():
    from xaal.lib import tools
    return {"title" : "Grid","devices":xaal_core.monitor.devices,"tools":tools,"active_menu":"grid"}


@route('/latency')
def socketio_latency_test():
    redirect('/static/latency.html')


@route('/links')
@view('links')
def links():
    return {'title':'Links'}


@get('/token/<profile>/<key>')
def set_token(profile,key):
    from .default import get_config_profile,build_cookie_token
    import time

    profile_cfg = get_config_profile(profile)
    if profile_cfg != {}:
        if key in profile_cfg.get('keys',[]):
            tmp =  build_cookie_token(profile,key)
            expires = time.time() + 60*60*24*365*2
            response.set_cookie('token',tmp,path='/',expires=expires)
        else:
            print("Invalid key")
    redirect('/')
