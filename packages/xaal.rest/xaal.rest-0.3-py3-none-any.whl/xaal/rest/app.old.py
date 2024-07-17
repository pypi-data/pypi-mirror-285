from gevent import monkey; monkey.patch_all(thread=False)


from xaal.lib import Engine,Device,helpers,tools,cbor
from xaal.monitor import Monitor

from bottle import default_app,debug,get,request,response,redirect,static_file

from . import json
import os
import platform
import logging

from gevent import Greenlet
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler


# dev-type that don't appear in results
BLACK_LIST=['cli.experimental',]

PACKAGE_NAME = "xaal.rest"
logger = logging.getLogger(PACKAGE_NAME)

# we use this global variable to share data with greenlet
monitor = None
cfg = None

def monitor_filter(msg):
    """ Filter incomming messages. Return False if you don't want to use this device"""
    if msg.dev_type in BLACK_LIST:
        return False
    return True

def setup_xaal():
    """ setup xAAL Engine & Device. And start it in a Greenlet"""
    global monitor,cfg
    engine = Engine()
    cfg = tools.load_cfg(PACKAGE_NAME)
    if not cfg:
        logger.info("No config file found, building a new one")
        cfg = tools.new_cfg(PACKAGE_NAME)
        cfg['config']['db_server'] = ''
        cfg['config']['port'] = 8080
        cfg.write()
    dev            = Device("hmi.basic")
    dev.address    = tools.get_uuid(cfg['config']['addr'])
    dev.vendor_id  = "IHSEV"
    dev.product_id = "REST API"
    dev.version    = 0.1
    dev.info       = "%s@%s" % (PACKAGE_NAME,platform.node())

    engine.add_device(dev)
    db_server = cfg['config'].get('db_server',None)
    if not db_server:
        logger.info('Please set a db_server in your config file')
    monitor = Monitor(dev,filter_func=monitor_filter,db_server=tools.get_uuid(db_server))
    engine.start()        
    green_let = Greenlet(xaal_loop, engine)
    green_let.start()

def xaal_loop(engine):
    """ xAAL Engine Loop Greenlet"""
    while 1:
        engine.loop()

def json_encode(obj):
    return json.dumps(obj,indent=4)        

def search_device(addr):
    dev = None
    uid = tools.str_to_uuid(addr)
    if uid:
        dev=monitor.devices.get_with_addr(uid)
    return dev

@get('/static/<filename:path>')
def send_static(filename):
    root = os.path.dirname(__file__)
    root = os.path.join(root,'static')
    return static_file(filename, root=root)

@get('/')
def goto_html():
    redirect('/static/index.html')

@get('/devices')
@get('/devices/')
def list_devices():
    """ Return the list of devices in JSON"""
    l = []
    for dev in monitor.devices:
        info = dev.description.get('info',None)
        vendor = dev.description.get('vendor_id',None)
        h = {'address':dev.address,'dev_type':dev.dev_type,'vendor':vendor,'info':info}
        l.append(h)
    cbor.cleanup(l)
    response.headers['Content-Type'] = 'application/json'
    return json_encode(l)

@get('/devices/<addr>')
def get_device(addr):
    """ Return the full description of a device """
    response.headers['Content-Type'] = 'application/json'
    dev = search_device(addr)
    if dev:
        res = {'address':dev.address,'dev_type':dev.dev_type}
        res.update({'attributes':dev.attributes})
        res.update({'description':dev.description})
        res.update({'metadata':dev.db})
        cbor.cleanup(res)
    else:
        res = {'error':{'code':404,'message':'Unknow device'}}
        response.status=404
    return json_encode(res)

@get('/devices/<addr>/<action>')
def send_request(addr,action):
    """ quick & dirty way to send request to device"""
    body = {}
    for k in request.query.keys():
        if k.endswith('_type'):
            continue
        value = request.query[k]
        tmp = '%s_type' % k
        if tmp in request.query.keys():
            type_ = request.query[tmp]
            if type_ == 'int':value = int(value)
            if type_ == 'float':value = float(value)
        body.update({k:value})

    response.headers['Content-Type'] = 'application/json'
    uid = tools.str_to_uuid(addr)
    dev = search_device(addr)
    if dev:
        monitor.engine.send_request(monitor.dev,[uid,],action,body)
        res = {'address':dev.address}
        cbor.cleanup(res)
    else:
        res = {'error':{'code':404,'message':'Unknow device'}}
        response.status=404
    return json_encode(res)

def run():
    """ start the xAAL stack & launch the HTTP stuff"""
    helpers.set_console_title(PACKAGE_NAME)
    helpers.setup_console_logger(level=logging.INFO)
    setup_xaal()
    app = default_app()
    debug(True)
    port = int(cfg.get('config').get('port',8080))
    logger.info("HTTP Server running on port : %d" % port)
    server = WSGIServer(("", port), app, handler_class=WebSocketHandler)
    server.serve_forever()

def main():
    try:
        run()
    except KeyboardInterrupt:
        print("Bye Bye...")
    
    
    
if __name__ == '__main__':
    main()
