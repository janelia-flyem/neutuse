import logging
import logging.handlers

from flask import Flask, render_template

from . import web
from . import apiv1

from .manager import Manager


class Server():

    '''
    This is the database server Class. 
    It initializes flask app, database backends, logging system and so on.
    '''
    
    def __init__(self, addr='127.0.0.1:5000', backend='sqlite:///test.db',
    enable_retry=False, debug=False, logfile='', email_config=None, slack_config =None):
        pos = addr.rfind(':')
        self.host, self.port = addr[:pos], addr[pos+1:]
        self.port = int(self.port)
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        self.debug = debug
        self.backend = backend
        self.logfile = logfile
        self.email_config = email_config
        self.slack_config = slack_config
        self.enable_retry = enable_retry
        
        self._init_manager()
        self._init_app()

    
    def _init_manager(self):
        Manager.set(backend=self.backend, enable_retry=self.enable_retry, logfile=self.logfile, email=self.email_config, slack=self.slack_config)
        Manager.get().logger.info('using {} as backend'.format(self.backend))

    def _init_app(self):
        self.app = Flask(__name__)
        self.app.config['addr'] = self.addr
        @self.app.route('/')
        def index():
    	    return render_template('index.html')
        self.app.register_blueprint(web.bp, url_prefix='/web')
        self.app.register_blueprint(apiv1.bp, url_prefix='/api/v1')
        Manager.get().logger.info('start database service at {}'.format(self.addr))
        
    def run(self):
        self.app.run(host=self.host, port=self.port, debug=True)

