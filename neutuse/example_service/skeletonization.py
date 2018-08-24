import os
import time
import json
import requests as rq

BASE_URL='http://127.0.0.1:5000/api/v1/tasks'

def getCmd(config):
    cmd=config['start_cmd']
    cmd+=' --command --skeletonize '
    cmd+=config['input']
    if 'bodyid' in config:
        cmd+=' --bodyid '+str(config['bodyid'])
    if 'output' in config:
        cmd+=' -o '+config['output']
    if 'force_update' in config and config['force_update']:
        cmd+=' --force'
    return cmd

def process(task):
    config=task['config']
    cmd=getCmd(config)
    print(cmd)
    rq.post(BASE_URL+'/'+str(task['id'])+'/comments',headers={'Content-Type':'application/json'},data=json.dumps('cmd:'+cmd))
    rq.post(BASE_URL+'/'+str(task['id'])+'/status/processing')
    rv=os.system(cmd)
    if rv==0:#success    
        rq.post(BASE_URL+'/'+str(task['id'])+'/status/done')
    else:
        rq.post(BASE_URL+'/'+str(task['id'])+'/status/failed')


def serve_forever():
    while True:
        rv=rq.get(BASE_URL+'/top/dvid/skeletonization/2')
        if rv.status_code==200 and len(rv.json())>0:
            for task in rv.json():
                process(task)                  
        else:
            print('no more tasks')
        time.sleep(5)
        
if __name__=='__main__':
    serve_forever()
