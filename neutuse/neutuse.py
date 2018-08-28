import sys
import json
import argparse

import requests as rq

from .taskman import TaskMan
from .service import Service



def run_taskman(addr, backend, debug=False):
    taskman = TaskMan(addr, backend, debug)
    taskman.run()


def run_service(name, addr, number=1):
    service = Service(name, addr, number)
    service.run()
    

def post_task(addr, data):
    if not addr.startswith('http'):
        addr = 'http://' + addr
    if not addr.endswith('/'):
        addr += '/'
    addr += 'api/v1/tasks'
    HEADERS={'Content-Type':'application/json'}
    rv = rq.post(addr, data=json.dumps(data), headers=HEADERS)
    print( rv.status_code )
    return rv.status_code == 200


def help():
    print('''
    Usage:
    1) Run task manager:
    neutuse run taskman [-a ADDR] [-b BACKEND] [-d]
    ADDR: Default is 127.0.0.1:5000
    BACKEND: Backend data base, default is sqlite:test.db
    -d debug mode'
    
    2) Run service:
    neutuse run service NAME [-a ADDR] [-n NUMBER]
    ADDR: which address the task manager is running
    Default ADDR is 127.0.0.1:5000
    NAME: specifies service name
    NUMBER: Numbers of tasks to fetch at each time
    
    3) Post task:
    neutuse post FILE [-a ADDR]
    ADDR: which address the task manager is running
    Default ADDR is 127.0.0.1:5000
    FILE: File describes the task
    ''')
    
    
def main(): 
    parser = argparse.ArgumentParser()
    num_args = len(sys.argv)
    
    if num_args <= 1:
        help()
    
    if sys.argv[1] == 'run' and num_args >= 3 :
        if sys.argv[2] == 'taskman':
            parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
            parser.add_argument('-d','--debug', action='store_true', default=False)
            parser.add_argument('-b','--backend', default='sqlite:db.db')
            args=parser.parse_args(sys.argv[3:])
            run_taskman(args.addr, args.backend, args.debug)
        elif sys.argv[2] == 'service':
            parser.add_argument('name', type=str)
            parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
            parser.add_argument('-n', '--number', type=int, default=1)
            args=parser.parse_args(sys.argv[3:])
            run_service(args.name, args.addr, args.number)
        else:
            help() 
    elif sys.argv[1] == 'post':
        parser.add_argument('file',type=str)
        parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
        args=parser.parse_args(sys.argv[2:])
        with open(args.file) as f:
            data=eval(f.read())    
        if post_task(args.addr, data):
            print('done')
        else:
            print('failed')
    else:
        help()
    

if __name__ == '__main__':
    main()
