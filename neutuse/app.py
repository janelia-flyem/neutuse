import os
import sys
import argparse

from flask import Flask

from api import task_manager_http_api_v1
import webclient
from service import Skeletonize


parser = argparse.ArgumentParser()
parser.add_argument('action',type=str, choices=['run', 'post'])
parser.add_argument('-t', '--type', type=str, choices=['taskmanager','service'])
parser.add_argument('-a', '--addr', type=str, default='127.0.0.1')
parser.add_argument('-p', '--port', type=int, default=5000)
parser.add_argument('-n', '--name', type=str, default='skeletonize')
args=parser.parse_args()


def run_taskmanager():
    app = Flask(__name__)
    webclient.init(args.addr, args.port)
    app.register_blueprint(task_manager_http_api_v1.bp, url_prefix='/api/v1/tasks')
    app.register_blueprint(webclient.bp, url_prefix='/client')
    app.run(host=args.addr, port=args.port)

def run_service():
    if args.name == 'skeletonize':
        Skeletonize(args.addr, args.port).run()
    else:
        print(name + ' service has not been supported yet')
    
if args.action == 'run':
    if args.type == 'taskmanager':
        run_taskmanager()
    elif args.type == 'service':
        run_service()
elif args.action == 'post':
    pass
