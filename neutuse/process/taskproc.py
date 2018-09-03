import json
import threading
import time
from abc import ABCMeta,abstractmethod
import logging
import logging.handlers

import requests as rq 

class TaskProcessor():
    
    '''
    This class is the base class of task processors.
    Subclasses should implement its own process function and its corresponding task's schema.
    The process function takes a task entity as parameters. It should call fail or success function
    to indicate whether the task has been susccessfully processed.
    '''
    
    __metaclass__ = ABCMeta
    
    '''Subclasses should define the __chema__ variable. It's used to verify tasks.'''
    __schema__ = {}
    
    
    def __init__(self, addr, type_, name, log_file='', num_workers=1):
        '''
        Args:
            addr(str): The address that database if running.
            type_(str): The type of tasks this class will process. 
            name(str): The name of tasks this class will process.
            log_file(str): Name of logging file.
            num_workers(int): Number of workers.
        '''
        self.addr = addr
        self.type = type_
        self.name = name
        self.num_workers = num_workers
        self.cur_num_workers = 0
        self.log_file = log_file
        self.lock = threading.Lock()
        self._init_logger()
        self._register()
        self._pulse()
    
    def _init_logger(self):
        self.logger = logging.getLogger('neutuse'+self.log_file)
        self.logger.setLevel(logging.INFO)
        fmt = "%(asctime)-15s %(levelname)s %(filename)s.%(lineno)d %(threadName)s>>>> %(message)s"
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(sh)
        if self.log_file != '':
            fh = logging.handlers.RotatingFileHandler(self.log_file,maxBytes = 1024*1024*100, backupCount = 3)    
            fh.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(fh)
    
    def _register(self):
    
        service = {'type':self.type,'name':self.name}
        rv = rq.post(self.addr + '/api/v1/services', headers={'Content-Type' : 'application/json'}, data=json.dumps(service))
        self.id = rv.json()['id']
        self.logger.info('Register service {}, status: {}'.format(json.dumps(service),str(rv.status_code == 200)))
        if rv.status_code != 200:
            self.logger.info(rv.text)
    
    def _pulse(self):
        rv = rq.post(self.addr + '/api/v1/services/{}/pulse'.format(self.id))
        self.logger.info('Pulse, status: {}'.format(str(rv.status_code  == 200)))
        if rv.status_code != 200:
            self.logger.info(rv.text)
            self._register()
        timer = threading.Timer(60, self._pulse)
        timer.start()
        
    def log(self, task, comment):
        url = self.addr + '/api/v1/tasks/{}/comments'.format(task['id'])
        rq.post(url, headers={'Content-Type' : 'application/json'}, data=json.dumps(comment))
    
    def _send_processing(self, task):
        url = self.addr + '/api/v1/tasks/{}/status/processing'.format(task['id'])
        rv = rq.post(url)
        self.logger.info('Send processing message for task {}, status: {}'.format(task['id'],str(rv.status_code ==200)))
        if rv.status_code !=200 :
            self.logger.info(rv.text)
        
    def fail(self, task):
        with self.lock:
            self.cur_num_workers -= 1
        url = self.addr + '/api/v1/tasks/{}/status/failed'.format(task['id'])
        rv = rq.post(url)
        self.logger.info('Send failed message for task {}, status: {}'.format(task['id'],str(rv.status_code ==200)))
        if rv.status_code !=200 :
            self.logger.info(rv.text)
        
    def success(self, task):
        with self.lock:
            self.cur_num_workers -= 1
        url = self.addr + '/api/v1/tasks/{}/status/done'.format(task['id'])
        rv = rq.post(url)
        self.logger.info('Send success message for task {}, status: {}'.format(task['id'],str(rv.status_code ==200)))
        if rv.status_code !=200 :
            self.logger.info(rv.text)
            
    def _verify(self, config):
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
                if self.cur_num_workers < self.num_workers:
                    cnt_to_fetch  = self.num_workers - self.cur_num_workers
                    query_url = self.addr + '/api/v1/tasks/top/{}/{}/{}'.format(self.type, self.name, cnt_to_fetch)
                    rv = rq.get(query_url)
                    self.logger.info('Fetch {} tasks from database, status: {}'.format(cnt_to_fetch, rv.status_code == 200))
                    if rv.status_code == 400:
                        self.logger.info(rv.text)
                    if rv.status_code == 200 and len(rv.json()) > 0:
                        tasks = []
                        for task in rv.json():
                            if self._verify(task['config']):
                                tasks.append(task)
                            else:
                                self.logger.info('Verify schema for task {} failed'.format(task['id']))
                                self.log(task,'invalid schema')
                                url = self.addr + '/api/v1/tasks/{}/status/failed'.format(task['id'])
                                rq.post(url)

                        for task in tasks:
                            self._send_processing(task)
                            with self.lock:
                                self.cur_num_workers += 1
                            self.logger.info('Start processing task {}'.format(task['id']))
                            threading.Thread(target=self.process, args=(task,)).start()
                    else:
                        time.sleep(10)
            except Exception as e:
                self.logger.error(e)
    
    @abstractmethod
    def process(self, task):
        pass
        

