import logging
import logging.handlers

from flask import Flask

from . import web
from . import apiv1

from .manager import Manager


class Server():

    '''
    This is the database server Class. 
    It initializes flask app, database backends, logging system and so on.
    '''
    
    def __init__(self, addr='127.0.0.1:5000', backend='sqlite:db.db',
    enable_retry=False, debug=False, log_file='', email_config=None, slack_config =None):
        pos = addr.rfind(':')
        self.host, self.port = addr[:pos], addr[pos+1:]
        self.port = int(self.port)
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        self.debug = debug
        self.enable_retry = enable_retry
        self._init_manager(backend, log_file, email_config, slack_config)
        self._init_app()

    
    def _init_manager(self, backend, logfile, email, slack):
        Manager.set(backend=backend, logfile=logfile, email=email, slack=slack)
        Manager.get().logger.info('using {} as backend'.format(backend))

    def _init_app(self):
        self.app = Flask(__name__)
        self.app.config['addr'] = self.addr
        self.app.register_blueprint(web.bp, url_prefix='/')
        self.app.register_blueprint(apiv1.bp, url_prefix='/api/v1')
        Manager.get().logger.info('start database service at {}'.format(self.addr))
        
        
    def run(self):
        self.app.run(host=self.host, port=self.port)

