import sys
import json
import argparse

import requests as rq

from .database import Server
from .process import Engine


def run_database(addr, backend, enable_retry= False, debug=False, log_file=''):    
    database = Server(addr, backend, enable_retry, debug, log_file)
    database.run()


def run_process(name, addr, log_file='', number=1):    
    engine = Engine(name, addr, log_file, number)
    engine.run()
    

def post_task(addr, data):
    if not addr.startswith('http'):
        addr = 'http://' + addr
    if not addr.endswith('/'):
        addr += '/'
    addr += 'api/v1/tasks'
    HEADERS={'Content-Type':'application/json'}
    rv = rq.post(addr, data=json.dumps(data), headers=HEADERS)
    print( rv.status_code )
    if rv.status_code !=200:
        print(rv.text)
    return rv.status_code == 200


def help():
    print('''
    Usage:
    1) Run database:
    neutuse run database [-a ADDR] [-b BACKEND] [-d DEBUG] [-r RETRY] [-l LOG]
    ADDR: Default is 127.0.0.1:5000
    BACKEND: Backend data base, default is sqlite:test.db
    DEBUG: debug mode
    RETRY: enable retry if tasks are expired
    LOG: Log file
    
    2) Run process:
    neutuse run process NAME [-a ADDR] [-n NUMBER] [-l LOG]
    ADDR: which address the database is running
    Default ADDR is 127.0.0.1:5000
    NAME: specifies the name of process
    NUMBER: Numbers of workers
    LOG: Log file
    
    3) Post task:
    neutuse post FILE [-a ADDR]
    ADDR: which address the database is running
    Default ADDR is 127.0.0.1:5000
    FILE: File describes the task
    ''')
    
    
def main(): 
    parser = argparse.ArgumentParser()
    num_args = len(sys.argv)
    
    if num_args <= 1:
        help()
        return
    
    if sys.argv[1] == 'run' and num_args >= 3 :
        if sys.argv[2] == 'database':
            parser.add_argument('-a', '--addr', default='127.0.0.1:5000')
            parser.add_argument('-d','--debug', action='store_true', default=False)
            parser.add_argument('-r','--retry', action='store_true', default=False)
            parser.add_argument('-b','--backend', default='sqlite:db.db')
            parser.add_argument('-l','--log', default='')
            args=parser.parse_args(sys.argv[3:])
            run_database(args.addr, args.backend, args.retry, args.debug, args.log)
        elif sys.argv[2] == 'process':
            parser.add_argument('name', type=str)
            parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
            parser.add_argument('-n', '--number', type=int, default=1)
            parser.add_argument('-l', '--log', default='')
            args=parser.parse_args(sys.argv[3:])
            run_process(args.name, args.addr, args.log, args.number)
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
        help()
    

if __name__ == '__main__':
    main()
