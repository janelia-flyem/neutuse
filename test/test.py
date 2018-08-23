import json
import requests as rq
from time import sleep

#task_api

def test_create():
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/'
    HEADERS={'Content-Type':'application/json'}
    rq.post(SERVER,data=json.dumps({'name':'skl','config':{'bodies':[1,2,3]},'life_span':1}),headers=HEADERS)
    rq.post(SERVER,data=json.dumps({'name':'asa','config':{'p1':1,'p2':{'p3':4}}}),headers=HEADERS)
    rq.post(SERVER,data=json.dumps({'name':'asa','config':{'p1':1,'p2':{'p3':'test'}}}),headers=HEADERS)
    rq.post(SERVER,data=json.dumps({'type':'test','life_span':3,'name':'sll','config':{'bodies':[1,2,3]}}),headers=HEADERS)
    rq.post(SERVER,data=json.dumps({'type':'test','life_span':30,'name':'sll','config':{'bodies':[1,2,3]}}),headers=HEADERS)
    rq.post(SERVER,data=json.dumps({'type':'test','life_span':60*10,'name':'sll','config':{'bodies':[1,2,3]}}),headers=HEADERS)

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
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/1/status/done'
    rv=rq.post(SERVER)
    print(rv)
    sleep(3)
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/1/status/failed'

    rv=rq.post(SERVER)
    print(rv)
    sleep(3)
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/1/status/processing'

    rv=rq.post(SERVER)
    print(rv)
    sleep(3)
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/1/status/asads'

    rv=rq.post(SERVER)
    print(rv)
    sleep(3)
    

def test_top():
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/top/dvid/asa/2'
    rv=rq.get(SERVER).json()
    print(rv)
    sleep(3)
    SERVER = 'http://127.0.0.1:5000/api/v1/tasks/top/test/sll/1'
    rv=rq.get(SERVER).json()
    print(rv)

if __name__=='__main__':
    test_create()
    test_query()
    test_update()
    #sleep(3)
    #test_top()
