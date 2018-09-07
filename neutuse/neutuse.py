import sys
import os
import json
import argparse
import threading
import requests as rq
import yaml

from .database import Server
from .process import Engine


__doc__ = '''Usage:

    1) Run database:
    neutuse run database [-a ADDR] [-b BACKEND] [-d DEBUG] [-r RETRY] [-l LOG] [-c CONFIG]
    ADDR: Address that the data base will be running, default is 127.0.0.1:5000.
    BACKEND: Backend of the data base, default is sqlite:test.db.
    DEBUG: Enable debug mode or not.
    RETRY: Enable retry mechanism or not. If this is turned on, expired tasks will be fetched again.
    LOG: Log file.
    CONFIG: Config file. If this option has been set, neutuse will load options from config file. 
    
    2) Run process:
    neutuse run process NAME [-a ADDR] [-n NUMBER] [-l LOG] [-c CONFIG]
    ADDR: Address that the data base is running, default is 127.0.0.1:5000.
    NAME: The name of the process to run.
    NUMBER: Numbers of workers.
    LOG: Log file.
    CONFIG: Config file. If this option has been set, neutuse will load options from config file.
    
    3) Post task:
    neutuse post FILE [-a ADDR]
    ADDR: Address the database is running, default is 127.0.0.1:5000.
    FILE: The name of file that describes the task.
'''


def run_database(addr, backend, enable_retry= False, debug=False, log_file='', email_config=None, slack_config=None):
    '''
    Args:
        addr(str): Which address the database will be running. Example: 127.0.0.1:5000
        backend(str): Which backend the database will be using. Example: Sqlite:test.db
        enable_retry(bool): If retry is enabled, expired tasks will be fetched by processes
        debug(bool): Enable debug mode or not
        log_file(str): Writing logs to which file.
        email_config(dict): Email config used to send and receive important information
    '''    
    database = Server(addr, backend, enable_retry, debug, log_file, email_config, slack_config)
    database.run()


def run_process(name, config):    
    '''
    Args:
        name(str): The name of process to run.
        config(dict): Configs passed to process
    '''
    services = [(name,config)]
    engine = Engine(services)
    engine.run()
    

def post_task(addr, data):
    '''
    Args:
        addr(str): Which address the database is running. Example: 127.0.0.1:5000
        data(dict): Task to post.
    Returns:
        bool: success or fail
    '''
    if not addr.startswith('http'):
        addr = 'http://' + addr
    if not addr.endswith('/'):
        addr += '/'
    addr += 'api/v1/tasks'
    HEADERS={'Content-Type':'application/json'}
    if not 'type' in data:
        data['type'] = 'default'
    if not 'name' in data:
        data['name'] = 'default'
    rv = rq.post(addr, data=json.dumps(data), headers=HEADERS)
    print( rv.status_code )
    if rv.status_code !=200:
        print(rv.text)
    return rv.status_code == 200


def help():
    print(__doc__)
    
    
def main(): 
    parser = argparse.ArgumentParser()
    num_args = len(sys.argv)
    
    if num_args <= 1:
        help()
        return
    
    if (sys.argv[1] == 'run' or sys.argv[1] == 'start') and num_args >= 3 :
    
        if sys.argv[2] == 'database':
            parser.add_argument('-c', '--config', default='')
            parser.add_argument('-a', '--addr', default='127.0.0.1:5000')
            parser.add_argument('-d','--debug', action='store_true', default=False)
            parser.add_argument('-r','--retry', action='store_true', default=False)
            parser.add_argument('-b','--backend', default='sqlite:test.db')
            parser.add_argument('-l','--log', default='')
            args=parser.parse_args(sys.argv[3:])
            if args.config != '':
                with open(args.config) as f:
                    config = yaml.load(f)
                    addr = config.get('address',{'host': '127.0.0.1', 'port':5000})
                    addr = addr['host'] + ':' + str(addr['port'])
                    backend = config.get('backend','sqlite:test.db')
                    log = config.get('log','')
                    retry = config.get('retry',False)
                    debug  = config.get('debug', False)
                    email = config.get('email',None)
                    slack = config.get('slack',None)
                    run_database(addr, backend, retry, debug, log, email, slack)
            else:
                run_database(args.addr, args.backend, args.retry, args.debug, args.log)
            
        elif sys.argv[2] == 'process':
            parser.add_argument('-c', '--config', default='')
            parser.add_argument('-n','--name', default = 'skeletonize')
            parser.add_argument('-a', '--addr',  default='127.0.0.1:5000')
            parser.add_argument('--number',  default=1)
            parser.add_argument('-l', '--log', default='')
            args=parser.parse_args(sys.argv[3:])
            if args.config != '':
                directory = os.path.split(args.config)[0]
                with open(args.config) as f:
                    config = yaml.load(f)
                    print(config)
                    addr = config.get('address',{'host': '127.0.0.1', 'port':5000})
                    addr = addr['host'] + ':' + str(addr['port'])
                    log = config.get('log','')
                    number = config.get('number',1)
                    processes = config.get('process', [])
                    threads = []
                    for p in processes:
                        if os.path.isabs(p['config']):
                            p_config = yaml.load(open(p['config']))
                        else:
                            p_config = yaml.load(open(os.path.join(directory, p['config'])))
                        name = p['name']
                        if 'log' not in p_config:
                            p_config['log'] = log
                        if 'number' not in p_config:
                            p_config['number'] = number
                        if 'address' not in p_config:
                            p_config['addr'] = addr
                        t = threading.Thread(target = run_process, args=(name, p_config))
                        threads.append(t)
                    for t in threads:
                        t.start()
            else:
                config = {'addr':args.addr, 'log': args.log, 'number': args.number}
                run_process(args.name, config)
        else:
            help() 

    elif sys.argv[1] == 'post':
        parser.add_argument('file')
        parser.add_argument('-a', '--addr', default='127.0.0.1:5000')
        args=parser.parse_args(sys.argv[2:])
        with open(args.file) as f:
            data=eval(f.read())    
        if post_task(args.addr, data):
            print('done')
    else:
        help()
    

if __name__ == '__main__':
    main()
