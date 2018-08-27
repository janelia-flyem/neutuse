import json
import requests as rq

SERVER='http://127.0.0.1:5000/api/v1/tasks/'

HEADERS={'Content-Type':'application/json'}

config={
    'output':'/home/deli/result.swc',
    'input':'/home/deli/t.tif',
    'force_update':True
    
}

rq.post(SERVER,data=json.dumps({'type':'dvid','name':'skeletonize','config':config}),headers=HEADERS)
rq.post(SERVER,data=json.dumps({'type':'dvid','name':'skeletonize','config':config}),headers=HEADERS)
rq.post(SERVER,data=json.dumps({'type':'dvid','name':'skeletonize','config':config}),headers=HEADERS)


config={
    'bodyid':1,
    'input':'address:port:uuid:labelvol',
    'force_update':True
    
}

rq.post(SERVER,data=json.dumps({'type':'dvid','name':'skeletonize','config':config}),headers=HEADERS)
rq.post(SERVER,data=json.dumps({'type':'dvid','name':'skeletonize','config':config}),headers=HEADERS)
rq.post(SERVER,data=json.dumps({'type':'dvid','name':'skeletonize','config':config}),headers=HEADERS)
