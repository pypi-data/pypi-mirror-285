from xaal.lib import tools
from .default import view,route
from .default import xaal_core as xaal


from bottle import get,response
import logging
import json
import requests

TOKEN=None
URL=None
CLASS = None


DAILY_REQ = """ [ $TOKEN '%s' { 'devid' '%s'  } NOW 49 h ] FETCH """

bindings = {'thermometer.basic' : 'temperature',
            'barometer.basic'   : 'pressure',
            'hygrometer.basic'  : 'humidity',
            'powermeter.basic'  : 'power',
            'co2meter.basic'  : 'co2',
            'luxmeter.basic'  : 'illuminance',
            }

logger = logging.getLogger(__name__)

def setup():
    global TOKEN,URL,CLASS
    cfg = tools.load_cfg(xaal.PACKAGE_NAME).get('config',None)
    if cfg:
        TOKEN = cfg.get('warp10_token',None)
        URL = cfg.get('warp10_url',None)
        CLASS = cfg.get('warp10_class',None)
        logger.warning("%s %s" % (URL,CLASS))

def init_req():
    return """'%s' 'TOKEN' STORE\n""" % (TOKEN)


def query(req):
    r = requests.post(URL,req)
    print(r)
    return r.text
    

def to_chartjs(data):
    r = []
    for tuple_ in data:
        date = round(tuple_[0] / 1000)
        value = tuple_[1]
        #r.append({"x": date, "y":value })
        r.append((date,value))
    return r

@get('/warp10/daily/<addr>')
def daily(addr):
    global CLASS
    response.headers['Content-Type'] = 'application/json'
    res = {}
    #import pdb;pdb.set_trace()
    dev=xaal.monitor.devices.get_with_addr(tools.get_uuid(addr))
    if dev:
        req = init_req()
        devtype = dev.dev_type
        var = bindings.get(devtype,None)
        if not var:
            return '{}'
        class_ = '%s.%s.%s' % (CLASS,devtype,var)
        tmp = DAILY_REQ % (class_,addr)
        req = init_req() + tmp
        data=query(req)
        
        res = json.loads(data)[0][0]['v']
    return json.dumps(to_chartjs(res))


@route('/warp10/graph/<addr>')
@view('graph')
def graph(addr):
    r = {"title" : "Warp10 daily","addr":addr}
    return r
