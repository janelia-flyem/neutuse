import os
import sys
import argparse

from taskman import TaskMan
from service import Skeletonize


parser = argparse.ArgumentParser()
parser.add_argument('action',type=str, choices=['run', 'post'])
parser.add_argument('-t', '--type', type=str, choices=['taskmanager','service'])
parser.add_argument('-a', '--addr', type=str, default='127.0.0.1')
parser.add_argument('-p', '--port', type=int, default=5000)
parser.add_argument('-n', '--name', type=str, default='skeletonize')
parser.add_argument('-d', '--debug', action='store_true', default=True)
args=parser.parse_args()


def run_taskmanager():
    taskman = TaskMan(host=args.addr, port=args.port, debug=args.debug)
    taskman.run()


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
