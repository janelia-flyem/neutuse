import logging
import logging.handlers

from flask import Flask

from . import webclient 
from .api import apiv1
from .storage import Sqlite
from .task import Task
from .taskmanager import TaskManager

class Server():

    '''
    This is the database server Class. 
    It initializes flask app, database backends, logging system and so on.
    '''
    
    def __init__(self, addr='127.0.0.1:5000', backend='sqlite:db.db',
    enable_retry=False, debug=False, log_file=''):
        pos = addr.rfind(':')
        self.host, self.port = addr[:pos], addr[pos+1:]
        self.port = int(self.port)
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        self.backend = backend
        self.debug = debug
        self.log_file = log_file
        self.enable_retry = enable_retry
        self._init_logger()
        self._init_app()

    
    def _init_logger(self):
        self.logger = logging.getLogger('neutuse')
        werk_logger = logging.getLogger('werkzeug')
        werk_logger.disabled = True
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
            
        fmt = "%(asctime)-15s %(levelname)s %(filename)s.%(lineno)d >>>> %(message)s"
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(sh)
        
        if self.log_file !='' :
            fh = logging.handlers.RotatingFileHandler(self.log_file,maxBytes = 1024*1024*100, backupCount = 3)    
            fh.setFormatter(logging.Formatter(fmt))
            werk_logger.addHandler(fh)
            self.logger.addHandler(fh)

    def _init_app(self):
        self.app = Flask(__name__)
        #print(self.app.logger)
        #self.app.logger = self.logger
        self.app.config['logger'] = self.logger
        self.app.config['addr'] = self.addr
        self.app.config['model'] = Task
        dbtype, path = self.backend.split(':')
        if dbtype == 'sqlite':
            db = Sqlite(path, Task)
        else:
            raise NotImplementedError(dbtype+' backend has not been implemented yet')
        
        self.app.config['db'] = db
        self.app.config['task_man'] = TaskManager(db, check_interval=10, waiting_time=5, enable_retry=self.enable_retry)
        
        self.app.register_blueprint(webclient.bp, url_prefix='/client')
        self.app.register_blueprint(apiv1.bp, url_prefix='/api/v1')
        
        self.logger.info('start database service at {}'.format(self.addr))
        self.logger.info('using {} as backend'.format(self.backend))
        
    def run(self):
        self.app.run(host=self.host, port=self.port)

