import sys,os
import json
import threading
import time
from abc import ABCMeta,abstractmethod
import logging
import logging.handlers
import traceback

import requests as rq 
from requests.exceptions import ConnectionError

from .neutuseurl import neutuse_url


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
    
    '''Subclasses should define __type_name__ variable.'''
    __type_name__= ('','')
    
    __description__ = ''
    
    __mode__ = 'pull'
    
    __push_url__ = ''
    
    def __init__(self, config):
        '''
        Args:
            addr(str): The address that database if running.
            log_file(str): Name of logging file.
            num_workers(int): Number of workers.
        '''
        self.type = self.__type_name__[0]
        self.name = self.__type_name__[1]
        self.config = config
        assert('addr' in config)
        self.addr = config['addr']
        if not self.addr.startswith('http'):
            self.addr = 'http://' + self.addr
        self.log_file = config.get('log','')
        self.num_workers = config.get('number',1)
        self.cur_num_workers = 0
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
        service = {'type':self.type, 'name':self.name, 'schema':self.__schema__,
                    'description':self.__description__, 'mode':self.__mode__, 'push_url':self.__push_url__}
        url = neutuse_url.get_service_registration_url(self.addr)
        rv = rq.post(url, headers={'Content-Type' : 'application/json'}, data=json.dumps(service))
        self.id = rv.json()['id']
        self.logger.info('Register service {}, status: {}'.format(json.dumps(service),str(rv.status_code == 200)))
        if rv.status_code != 200:
            self.logger.info(rv.text)
    
    def _maybe_exit(self):
        try:
            rv = rq.get(neutuse_url.get_service_url(self.addr,self.id))
            status = rv.json()['status']
            if status == 'killed':
                self.logger.info('Shutting down...')
                os._exit(0)
        except Exception as e:
            self.logger.info(e)
        
    def _pulse(self):
        try:
            self._maybe_exit()
            rv = rq.post(neutuse_url.get_service_pulse_url(self.addr,self.id))
            self.logger.info('Pulse, status: {}'.format(str(rv.status_code  == 200)))
            if rv.status_code != 200:
                self.logger.info(rv.text)
                self._register()
        except Exception as e:
            self.logger.info(e)
        finally:
            timer = threading.Timer(10, self._pulse)
            timer.setDaemon(True)
            timer.start()
        
    def log(self, task, comment):
        url = neutuse_url.get_task_comment_url(self.addr,task['id'])
        rq.post(url, headers={'Content-Type' : 'application/json'}, data=json.dumps(comment))
    
    def ack(self, task):
        url = neutuse_url.get_task_ack_url(self.addr, task['id'], self.id)
        rv = rq.post(url)
        self.logger.info('Send processing message for task {}, status: {}'.format(task['id'],str(rv.status_code ==200)))
        if rv.status_code !=200 :
            self.logger.info(rv.text)
        
    def fail(self, task):
        with self.lock:
            self.cur_num_workers -= 1
        url = neutuse_url.get_task_fail_url(self.addr,task['id'], self.id)
        rv = rq.post(url)
        self.logger.info('Send failed message for task {}, status: {}'.format(task['id'],str(rv.status_code ==200)))
        if rv.status_code !=200 :
            self.logger.info(rv.text)
        
    def success(self, task):
        with self.lock:
            self.cur_num_workers -= 1
        url = neutuse_url.get_task_success_url(self.addr,task['id'], self.id)
        rv = rq.post(url)
        self.logger.info('Send success message for task {}, status: {}'.format(task['id'],str(rv.status_code ==200)))
        if rv.status_code !=200 :
            self.logger.info(rv.text)
            
    def _verify(self, config):
        for key in self.__schema__:
            if (self.__schema__[key]['required']):
                if key not in config:
                    return False
                if type(config[key]).__name__ !=  self.__schema__[key]['type']:
                    return False
            else:
                if key in config:
                    if type(config[key]).__name__ !=  self.__schema__[key]['type']:
                        return False
        return True
             
    def _fetch_tasks(self):
        cnt_to_fetch  = self.num_workers - self.cur_num_workers
        query_url = neutuse_url.get_task_topk_url(self.addr, self.type, self.name, cnt_to_fetch)
        rv = rq.get(query_url)
        self.logger.info('Fetch {} tasks from database, status: {}'.format(cnt_to_fetch, rv.status_code == 200))
        if rv.status_code == 200:
            return rv.json()
        self.logger.info(rv.text)
        return []

    def run(self):
        while True:
            try:
                if self.cur_num_workers < self.num_workers:
                    rv = self._fetch_tasks()
                    if len(rv) > 0:
                        tasks = []
                        for task in rv:
                            if self._verify(task['config']):
                                tasks.append(task)
                            else:
                                self.logger.info('Verify schema for task {} failed'.format(task['id']))
                                self.log(task,'invalid schema')
                                url = neutuse_url.get_task_fail_url(self.addr, task['id'], self.id)
                                rq.post(url)
                        for task in tasks:
                            self.ack(task)
                            with self.lock:
                                self.cur_num_workers += 1
                            self.logger.info('Start processing task {}'.format(task['id']))
                            threading.Thread(target=self.process, args=(task,)).start()
                    else:
                        time.sleep(10)
            except ConnectionError as e:
                self.logger.error(e)
                time.sleep(60*3)
            except Exception as e:
                traceback.print_tb(e)
                self.logger.error(e)
    
    @abstractmethod
    def process(self, task):
        pass
        

