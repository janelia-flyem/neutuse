import os
import sys
import argparse

from taskman import TaskMan
from service import Service


parser = argparse.ArgumentParser()
parser.add_argument('action',type=str, choices=['run'])
parser.add_argument('-t', '--type', type=str, choices=['taskmanager','service'])
parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
parser.add_argument('-n', '--name', type=str, default='skeletonize')
parser.add_argument('-d', '--debug', action='store_true', default=False)
args=parser.parse_args()


def run_taskmanager():
    taskman = TaskMan(addr=args.addr, debug=args.debug)
    taskman.run()


def run_service():
    service = Service(name=args.name, addr=args.addr)
    service.run()

def post_task():
    pass
    
if args.action == 'run':
    if args.type == 'taskmanager':
        run_taskmanager()
    elif args.type == 'service':
        run_service()
