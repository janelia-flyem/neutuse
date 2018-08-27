import json
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
    
    def log(self, comment):
        comment_url = self.addr + '/api/v1/tasks/{}/comments'.format(self.current_id)
        rq.post(comment_url, headers={'Content-Type' : 'application/json'}, data=json.dumps(comment))

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
                for task in rv.json():
                    confirm_url = self.addr + '/api/v1/tasks/{}/status/processing'.format(task['id'])
                    success_url = self.addr + '/api/v1/tasks/{}/status/done'.format(task['id'])
                    fail_url = self.addr + '/api/v1/tasks/{}/status/failed'.format(task['id'])
                    if self.verify(task['config']):    
                        rq.post(confirm_url)
                        self.current_id = task['id']
                        if self.process(task['config']):
                            
                            rq.post(success_url)
                        else:
                            
                            rq.post(fail_url)
                    else:
                        rq.post(fail_url)
                        print('invalid task schema')
    
    @abstractmethod
    def process(self, config):
        pass
        

