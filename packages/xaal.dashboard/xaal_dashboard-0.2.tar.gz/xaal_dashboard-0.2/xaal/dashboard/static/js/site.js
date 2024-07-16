var tags = {};
var evt_bus = null;
var sio = null;

//================ JS tools ====================================================
// dumbs functions to mimic jQuery selectors
var _ = function ( elem ) {
  return document.querySelector( elem );
}

var __ = function ( elem ) {
  return document.querySelectorAll( elem );
}

// check if we use a mobile user-agent
function detectMobile() {
 if( navigator.userAgent.match(/Android/i)
 || navigator.userAgent.match(/webOS/i)
 || navigator.userAgent.match(/iPhone/i)
 || navigator.userAgent.match(/iPad/i)
 || navigator.userAgent.match(/iPod/i)
 || navigator.userAgent.match(/BlackBerry/i)
 || navigator.userAgent.match(/Windows Phone/i)
 ){
    return true;
  }
 else {
    return false;
  }
}

//================ Event stuffs  ===============================================
function EventBus () {
    riot.observable(this);
    this.mounted = false;
    this.connected = false;

    this.on('sio-connect',function() {
        log('Event : connected ' + sio.io.engine.transport.name);
        this.connected = true;
        this.refresh_attributes();
    });

    this.on('sio-disconnect',function() {
        log('Event : disconnected');
        this.connected = false;
    });

    this.on('tags-mount',function() {
        log('Event : mounted');
        this.mounted = true;
        run_sio();
        //this.refresh_attributes();
    });

    this.on('visible',function() {
        log('Event : visible');
        this.refresh_attributes();
    });

    this.refresh_attributes = function() {
        if ((this.connected == true) && (this.mounted == true)) {
            sio_refresh_attributes();
        }
    }
};

function visibilityChanged(data) {
    if (document.visibilityState == 'visible')
        evt_bus.trigger('visible');
    else
        console.log('visibility => ' + document.visibilityState);
}


function log(msg) {
    //elt = _('#messages');
    //elt.innerText = elt.innerText +"\n" + msg;
    //elt.style.color = 'green';
    console.log(msg)
}

function display_tags() {
    for (t in tags) {
        tag = tags[t];
        console.log(t + " " + tag.addr + " : " +  tag.opts.dataIs);    
    }


}

//================ SocketIO ================================================
function run_sio() {
    //sio = io.connect('ws://' + document.domain + ':' + location.port,{transports: ['websocket'],forceNew:true});
    sio = io({transports: ['websocket'],forceNew:true});
    sio.on('connect', function() {
        evt_bus.trigger('sio-connect');
    });

    sio.on('disconnect', function() {
        evt_bus.trigger('sio-disconnect');
    });

    sio.on('event_attributeChanges', function(data) {
        for (t in tags) {
            var attrs = tags[t].root.attributes;
            if (attrs.hasOwnProperty('xaal_addr')) {
                if (attrs.xaal_addr.value == data['address']) {
                    tags[t].receive(data);
                    //console.log('Evt attr for : ' + data['address']);
                }
            }
        }
    });
}


//================ refresh attributes  =======================================
// the old refresh_attributes blocks the page rendering process.
function sio_refresh_attributes_old() {
    console.log('refresh_attributes');
    var addrs = [];
    for (t in tags) {
        var attrs = tags[t].root.attributes;
        if (attrs.hasOwnProperty('xaal_addr')) {
            addrs.push(attrs.xaal_addr.value);
        }
    }
    sio.emit('refresh_attributes',addrs);
}

function sio_refresh_attributes() {
    console.log('refresh_attributes');
    for (t in tags) {
        var attrs = tags[t].root.attributes;
        if (attrs.hasOwnProperty('xaal_addr')) {
            sio.emit('query_attributes',attrs.xaal_addr.value);
        }
    }
}

function sio_send_request(addr,action,body) {
    //console.log('Sending :' + addr + ' ' + action + ' ' + body);
    sio.emit('send_request',addr,action,body);
}

function sio_query_attributes(addr) {
    //console.log('query '+ addr);
    sio.emit('query_attributes',addr);
}


//================ Main ========================================================
evt_bus = new EventBus();

riot.compile(function() {
    tags = riot.mount('*');
    evt_bus.trigger('tags-mount');
})

// We need to force sync the content if we use a mobile device.
// mobile device need a refresh when it come back from sleep
if (detectMobile() == true) {
    document.addEventListener("visibilitychange", visibilityChanged);
}
