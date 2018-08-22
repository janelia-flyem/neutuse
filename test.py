import requests as rq

#task_api
SERVER = 'http://127.0.0.1:5000/api/v1/tasks/'
rq.get(SERVER)
payload = {'name':'skeletonization','type':'dvid'}
rq.get(SERVER,params=payload)
rq.get(SERVER + '1')
rq.get(SERVER + '1/name')
rq.post(SERVER,data={'name':'skl','type':'dvid'})
rq.post(SERVER+'1',data={'name':'skl'})
