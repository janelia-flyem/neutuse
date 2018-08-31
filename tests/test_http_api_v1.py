'''
    This File tests neutuse HTTP APIS version 1.
    If everything is fine, you should see 'OK' at the bottom of the screen.
'''

import unittest
import json
import threading
import time
import requests as rq

import neutuse


ADDR = '127.0.0.1:8080'
JSON_HEADER = {'Content-Type':'application/json'} 
BASE_URL = 'http://'+ ADDR + '/api/v1/'

    
class TestNeutuseHTTPAPIV1(unittest.TestCase):
        
    def test_post_tasks(self):
        url  = BASE_URL + 'tasks'
        task = {
                'type':'dvid',
                'name':'skeletonize',
                'description':'test',
                'config':{'input':'test','bodyid':1},
                'life_span':3600,
                'max_tries':1,
                'user':'test'
                }
        rv = rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        self.assertEqual(rv.status_code,200)

        task = {
                'type':'dvid',
                'name':'skeletonize',
                'config':{'input':'test','bodyid':1},
                'wrong':'wrong'
                }
        rv = rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        self.assertEqual(rv.status_code,400)
        
        task = {
                'wrong':'dvid',
                'name':'skeletonize',
                'config':{'input':'test','bodyid':1}
                }
        rv = rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        self.assertEqual(rv.status_code,400)
        
        task = {
                'type':'dvid',
                'name':'skeletonize',
                'config': 'wrong'
                }
        rv = rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        self.assertEqual(rv.status_code,400)

        task = {
                'type':'dvid',
                'config': 'wrong'
                }
        rv = rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        self.assertEqual(rv.status_code,400)
        
    def test_get_tasks(self):
        url  = BASE_URL + 'tasks'
        task = {
                'type':'abc',
                'name':'skeletonize',
                'description':'test',
                'config':{'input':'test','bodyid':1},
                'life_span':300,
                'max_tries':100,
                'user':'test'
                }
        rv_task = rq.post(url, data=json.dumps(task), headers=JSON_HEADER).json()
        rv = rq.get(url,params={'id':rv_task['id']})
        self.assertEqual(rv.status_code,200)
        self.assertEqual(len(rv.json()),1)
        task = rv.json()[0]
        for key in task:
            self.assertEqual(task[key], rv_task[key])
        
        rv = rq.get(url,params={'id':rv_task['id'],'name':'skeletonize'})
        self.assertEqual(rv.status_code,200)
        self.assertEqual(len(rv.json()),1)
        task = rv.json()[0]
        for key in task:
            self.assertEqual(task[key], rv_task[key])
 
        rv = rq.get(url,params={'ids':rv_task['id']})
        self.assertEqual(rv.status_code,400)
        
        rv = rq.get(url,params={'id':rv_task['id'],'name':'skeletonze'})
        self.assertEqual(rv.status_code,400)
                    
    def test_get_task_by_id(self):
        url  = BASE_URL + 'tasks'
        task = {
                'type':'abc',
                'name':'skeletonize',
                'config':{'input':'test','bodyid':1},
                }
        rv_task = rq.post(url, data=json.dumps(task), headers=JSON_HEADER).json()
        rv = rq.get(url+'/{}'.format(rv_task['id']))
        self.assertEqual(rv.status_code,200)
        task = rv.json()
        for key in task:
            self.assertEqual(task[key], rv_task[key])
        rv = rq.get(url+'/{}'.format(101011123))
        self.assertEqual(rv.status_code,400)
      
    def test_get_task_property_by_id(self):
        url  = BASE_URL + 'tasks'
        task = {
                'type':'abc',
                'name':'skeletonize',
                'config':{'input':'test','bodyid':1},
                }
        rv_task = rq.post(url, data=json.dumps(task), headers=JSON_HEADER).json()
        rv = rq.get(url+'/{}/config'.format(rv_task['id']))
        self.assertEqual(rv.status_code,200)
        config = rv.json()
        self.assertEqual(task['config'],config)
        rv = rq.get(url+'/{}/as'.format(rv_task['id']))
        self.assertEqual(rv.status_code,400)
        
    def test_top_k_tasks(self):
        url  = BASE_URL + 'tasks'
        task = {
                'type':'dvid',
                'name':'skeletonize',
                'config':{'input':'test','bodyid':1},
                'priority':1000,
                'description':'1'
                }
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        task['priority'] = 1001
        task['description'] ='2'
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        task['priority'] = 1001
        task['description'] ='3'
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        task['priority'] = 9999
        task['description'] ='4'
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)

        rv = rq.get(url+'/top/dvid/skeletonize/4')
        self.assertEqual(rv.status_code,200)
        self.assertEqual(len(rv.json()),4)        
        self.assertEqual(rv.json()[0]['description'],'4')
        self.assertEqual(rv.json()[1]['description'],'2')
        self.assertEqual(rv.json()[2]['description'],'3')
        self.assertEqual(rv.json()[3]['description'],'1')

        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        task['priority'] = 10001
        task['description'] ='20'
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        task['description'] = 10001
        task['description'] ='30'
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        task['priority'] = 99999
        task['description'] ='40'
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
                
        rq.post(url, data=json.dumps(task), headers=JSON_HEADER)
        rv = rq.get(url+'/top/dvid/skeletonize/1')
        self.assertEqual(len(rv.json()),1)
        rv = rq.get(url+'/top/dvid1/skeletonize/1')
        self.assertEqual(rv.status_code,400)
        rv = rq.get(url+'/top/dvid/skeletonize2/1')
        self.assertEqual(rv.status_code,400)
        
    def test_post_task_status(self):
        url  = BASE_URL + 'tasks'
        task = {
                'type':'abc',
                'name':'skeletonize',
                'config':{'input':'test','bodyid':1},
                }
        rv_task = rq.post(url, data=json.dumps(task), headers=JSON_HEADER).json()
        rv = rq.post(url+'/{}/status/processing'.format(rv_task['id']))
        self.assertEqual(rv.status_code,200)
        self.assertEqual(rv.json()['status'],'processing')
        
        rv = rq.post(url+'/{}/status/failed'.format(rv_task['id']))
        self.assertEqual(rv.status_code,200)
        self.assertEqual(rv.json()['status'],'failed')
        
        rv = rq.post(url+'/{}/status/done'.format(rv_task['id']))
        self.assertEqual(rv.status_code,200)
        self.assertEqual(rv.json()['status'],'done')
        
        rv = rq.post(url+'/{}/status/processings'.format(rv_task['id']))
        self.assertEqual(rv.status_code,400)
        
    def test_post_task_comments(self):
        url  = BASE_URL + 'tasks'
        task = {
                'type':'abc',
                'name':'skeletonize',
                'config':{'input':'test','bodyid':1},
                }
        rv_task = rq.post(url, data=json.dumps(task), headers=JSON_HEADER).json()
        rv = rq.get(url+'/{}/comments'.format(rv_task['id'])).json()
        self.assertEqual(rv,[])
        rq.post(url+'/{}/comments'.format(rv_task['id']), data='123', headers=JSON_HEADER)
        rv = rq.get(url+'/{}/comments'.format(rv_task['id'])).json()
        self.assertEqual(rv,['123'])
        rq.post(url+'/{}/comments'.format(rv_task['id']), data='456', headers=JSON_HEADER)
        rv = rq.get(url+'/{}/comments'.format(rv_task['id'])).json()
        self.assertEqual(rv,['123','456'])
              
   
if __name__ == '__main__':
    threading.Thread(target = neutuse.run_database, args=(ADDR, 'sqlite:{}.db'.format(time.time()))).start()
    time.sleep(1)
    unittest.main()
