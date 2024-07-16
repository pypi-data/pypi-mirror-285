import rapidjson

"""
Since version 0.7 xAAL msg are CBOR encoded, this means w/ addresses now
use Cbor UUID tag. So to avoid error w/ JSON encoder of UUID, we need to 
use rapidjson that provide UUID to JSON. This wrapper module provide this
to sio package.
"""

def dumps(*args,**kwargs):
    obj = args[0]
    return rapidjson.dumps(obj,uuid_mode=rapidjson.UM_CANONICAL)        


loads = rapidjson.loads
