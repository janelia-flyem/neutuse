import json
import threading
import time
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
        self.num_workers = 0
        self.lock = threading.Lock()
        self.register()
        self.pulse()
    
    def register(self):
        service = {'type':self.type,'name':self.name}
        rv = rq.post(self.addr + '/api/v1/services', headers={'Content-Type' : 'application/json'}, data=json.dumps(service))
        self.id = rv.json()['id']
    
    def pulse(self):
        rv = rq.post(self.addr + '/api/v1/services/{}/pulse'.format(self.id))
        if rv.status_code != 200:
            self.register()
        timer = threading.Timer(60, self.pulse)
        timer.start()
        
    def log(self, task, comment):
        url = self.addr + '/api/v1/tasks/{}/comments'.format(task['id'])
        rq.post(url, headers={'Content-Type' : 'application/json'}, data=json.dumps(comment))
    
    def _send_processing(self, task):
        url = self.addr + '/api/v1/tasks/{}/status/processing'.format(task['id'])
        rq.post(url)
        
    def fail(self, task):
        with self.lock:
            self.num_workers -= 1
        url = self.addr + '/api/v1/tasks/{}/status/failed'.format(task['id'])
        rq.post(url)
        
    def success(self, task):
        with self.lock:
            self.num_workers -= 1
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
            try:
                if self.num_workers < self.cnt:
                    cnt_to_fetch  = self.cnt - self.num_workers
                    query_url = self.addr + '/api/v1/tasks/top/{}/{}/{}'.format(self.type, self.name, cnt_to_fetch)
                    rv = rq.get(query_url)
                    
                    if rv.status_code == 200 and len(rv.json()) > 0:
                        tasks = []
                        for task in rv.json():
                            if self.verify(task['config']):
                                tasks.append(task)
                            else:
                                self.log(task,'invalid schema')
                                url = self.addr + '/api/v1/tasks/{}/status/failed'.format(task['id'])
                                rq.post(url)

                        for task in tasks:
                            self._send_processing(task)
                            with self.lock:
                                self.num_workers += 1
                            threading.Thread(target=self.process, args=(task,)).start()
                    else:
                        time.sleep(3)
            except Exception as e:
                print(e)
    
    @abstractmethod
    def process(self, task):
        pass
        

