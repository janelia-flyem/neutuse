import os
import sys

from flask import Flask

from api import task_manager_http_api_v1
import webclient
from service import run_service

def run_app(host,port):
    app = Flask(__name__)
    webclient.init(host,port)
    app.register_blueprint(task_manager_http_api_v1.bp,url_prefix='/api/v1/tasks')
    app.register_blueprint(webclient.bp,url_prefix='/client')
    app.run(host=host,port=port)

if __name__ == '__main__':    
    mode = sys.argv[1]
    if mode == 'taskmanager':
        host,port = sys.argv[2].split(':')
        port = int(port)
        run_app(host,port)
    elif mode == 'service':
        name = sys.argv[2]
        host,port = sys.argv[3].split(':')
        port=int(port)
        run_service(name,host,port)
