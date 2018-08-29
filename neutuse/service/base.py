import json
from multiprocessing import Pool
from abc import ABCMeta,abstractmethod

import requests as rq 

class Base():
    
    __metaclass__ = ABCMeta
    __chema__ = {}
    
    def __init__(self, addr, type_, name, cnt=1):
        self.addr = addr
        self.type = type_
        self.name = name
        self.cnt = cnt
    
    def log(self, task, comment):
        url = self.addr + '/api/v1/tasks/{}/comments'.format(task['id'])
        rq.post(url, headers={'Content-Type' : 'application/json'}, data=json.dumps(comment))
    
    def _send_processing(self, task):
        url = self.addr + '/api/v1/tasks/{}/status/processing'.format(task['id'])
        rq.post(url)
        
    def fail(self, task):
        url = self.addr + '/api/v1/tasks/{}/status/failed'.format(task['id'])
        rq.post(url)
        
    def success(self, task):
        url = self.addr + '/api/v1/tasks/{}/status/done'.format(task['id'])
        rq.post(url)
        
    def verify(self, config):
        for key in self.__schema__:
            if (self.__schema__[key]['required']):
                if key not in config:
                    return False
                if not isinstance(config[key], self.__schema__[key]['type']):
                    return False
            else:
                if key in config:
                    if not isinstance(config[key], self.__schema__[key]['type']):
                        return False
        return True
              
    def run(self):
        while True:
            query_url = self.addr + '/api/v1/tasks/top/{}/{}/{}'.format(self.type, self.name, self.cnt)
            rv = rq.get(query_url)
            
            if rv.status_code == 200 and len(rv.json()) > 0:
                tasks = []
                for task in rv.json():
                    if self.verify(task['config']):
                        tasks.append(task)
                    else:
                        self.log(task,'invalid schema')
                        self.fail(task)
                with Pool(len(tasks)) as p:
                    for task in tasks:
                        self._send_processing(task)
                    p.map(self.process,tasks)
    
    @abstractmethod
    def process(self, task):
        pass
        

