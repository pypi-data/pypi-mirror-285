from bottle import route,request
from ..core import xaal_core
from bottle import mako_template as template
import functools


def build_cookie_token(profile,key):
    import hashlib
    ua = request.environ.get('HTTP_USER_AGENT')
    buf = '%s/%s/%s' % (ua,profile,key)
    h = hashlib.blake2b(buf.encode('utf-8')).hexdigest()
    return h

def search_token_profile(token):
    """search the profile for a given token"""
    profiles = xaal_core.config.get('profiles',{})
    for p in profiles:
        for k in profiles[p].get('keys',[]):
            h = build_cookie_token(p,k)
            if h == token:
                return profiles[p]
    return {}

def get_config_profile(name):
    return xaal_core.config.get('profiles',{}).get(name,{})

def get_profile():
    return search_token_profile( request.get_cookie('token') )

def view(tpl_name,**defaults):
    # this is a cut / paste from the bottle view. 
    # just tweak it to support custom template from profile
    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, dict):
                tplvars = defaults.copy()
                tplvars.update(result)
                profile = get_profile()
                tmpl = profile.get('%s_tmpl' %tpl_name,'%s.mako' % tpl_name)
                tplvars.update({'profile':profile})
                return template(tmpl, **tplvars)
            elif result is None:
                return template(tpl_name, defaults)
            return result

        return wrapper

    return decorator
