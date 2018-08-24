import os
import time
import json
import requests as rq


class Skeletonize():
    
    def __init__(self,host,port):
        self.url='http://'+str(host)+':'+str(port)+'/api/v1/tasks'
    
    def _get_cmd(self,config):
        cmd=config['start_cmd']
        cmd+=' --command --skeletonize '
        cmd+=config['input']
        if 'force_update' in config and config['force_update']:
            cmd+=' --force '
        if 'bodyid' in config:
            cmd+=' --bodyid '+str(config['bodyid'])
        if 'output' in config:
            cmd+=' -o '+config['output']
        return cmd
        
    def _process(self,task):
        config=task['config']
        cmd=self._get_cmd(config)
        print(cmd)
        rq.post(self.url+'/'+str(task['id'])+'/comments',headers={'Content-Type':'application/json'},data=json.dumps('cmd:'+cmd))
        rq.post(self.url+'/'+str(task['id'])+'/status/processing')
        rv=os.system(cmd)
        if rv==0:#success    
            rq.post(self.url+'/'+str(task['id'])+'/status/done')
        else:
            rq.post(self.url+'/'+str(task['id'])+'/status/failed')
        
    def run(self):
        while True:
            rv=rq.get(self.url+'/top/dvid/skeletonize/1')
            if rv.status_code==200 and len(rv.json())>0:
                for task in rv.json():
                    self._process(task)
        
