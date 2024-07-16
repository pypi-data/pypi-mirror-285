import rapidjson
from xaal.lib import bindings

"""
Since version 0.7 xAAL msg are CBOR encoded, this means w/ addresses now
use Cbor UUID tag. So to avoid error w/ JSON encoder of UUID, we need to 
use rapidjson that provide UUID to JSON. This wrapper module provide this
to sio package.
"""

def dumps(*args,**kwargs):
    obj = args[0]
    try:
        r = rapidjson.dumps(obj,uuid_mode=rapidjson.UM_CANONICAL)        
    except TypeError:
        import pdb;pdb.set_trace()
    return r


def cleanup(obj):
    """ 
    recursive walk a object to search for un-wanted CBOR tags.
    Transform this tag in string format, this can be UUID, URL..

    /!\ use with caution, this operate in-place changes.

    This is quite the same code as cbor.cleanup() but simply call
    get() instead of str() 
    """
    if isinstance(obj,list):
        for i in range(0,len(obj)):
            obj[i] = cleanup(obj[i]) 
        return obj

    if isinstance(obj,dict):
        for k in obj.keys():
            obj.update({k:cleanup(obj[k])})
        return obj

    if type(obj) in bindings.classes:
        r = obj.get()
        return r
    else:
        return obj

def prepare_cbor(obj):
    """ transfor a cbor object into something that rapdjson can handle """
    import copy
    r = copy.deepcopy(obj)
    return cleanup(r)

loads = rapidjson.loads

