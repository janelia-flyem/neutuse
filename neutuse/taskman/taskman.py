from flask import Flask
from . import webclient 
from .api import apiv1
from .storage import Sqlite
from .task import Task
from .man import Man

class TaskMan():
    
    def __init__(self, addr, backend, enable_retry, debug):
        self.host, self.port = addr.split(':')
        self.port = int(self.port)
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        self.backend = backend
        self.debug = debug
        self.enable_retry = enable_retry
        self._initApp()
        
    def _initApp(self):
        self.app = Flask(__name__)
        
        self.app.config['addr'] = self.addr
        self.app.config['model'] = Task
        
        dbtype, path = self.backend.split(':')
        if dbtype == 'sqlite':
            db = Sqlite(path, Task)
        else:
            raise NotImplementedError(dbtype+' backend has not been implemented yet')
        
        self.app.config['db'] = db
        self.app.config['task_man'] = Man(db, check_interval=10, waiting_time=5, enable_retry=self.enable_retry)
        
        self.app.register_blueprint(webclient.bp, url_prefix='/client')
        self.app.register_blueprint(apiv1.bp, url_prefix='/api/v1')
        
        
    def run(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)

