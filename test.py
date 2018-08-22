import json
import requests as rq
from time import sleep

#task_api

def test_create():
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/'
    HEADERS={'Content-Type':'application/json'}
    rq.post(SERVER,data=json.dumps({'name':'skl','config':{'bodies':[1,2,3]}}),headers=HEADERS)
    rq.post(SERVER,data=json.dumps({'type':'dvid','life_span':1,'name':'sll','config':{'bodies':[1,2,3]}}),headers=HEADERS)

def test_query():
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/'
    HEADERS={'Content-Type':'application/json'}
    rv=rq.get(SERVER).json()
    for i in rv:
        print(i)
    rv=rq.get(SERVER,params={'name':'sll'}).json()
    for i in rv:
        print(i)
    rv=rq.get(SERVER+'1').json()
    print(rv)
    rv=rq.get(SERVER+'1/name').json()
    print(rv)

def test_update():
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/'
    HEADERS={'Content-Type':'application/json'}
    rv=rq.post(SERVER+'1',headers=HEADERS,data=json.dumps({'name':'sss'})).json()
    print(rv)

def test_top():
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/top/2'
    rv=rq.get(SERVER).json()
    print(rv)

    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/top/1'
    rv=rq.get(SERVER).json()
    print(rv)

if __name__=='__main__':
    test_top()
