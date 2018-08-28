import sys
import json
import argparse

import requests as rq

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


if  __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file',type=str)
    parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
    args=parser.parse_args()
    
    with open(args.file) as f:
        data=eval(f.read())    
    if post_task(args.addr, data):
        print('done')
    else:
        print('failed')
