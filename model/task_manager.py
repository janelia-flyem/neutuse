import time
import heapq
import threading
from config import db
from storage.op import And,Or,Not,Equal,Greater

class TaskManager():

    def __init__(self):
        timer=threading.Timer(10,self._routine)
        timer.start()

    def insert(self,task):
        task.id=db.next_available_id()
        return db.insert(task)

    def query(self,filters):
        fs=[ Equal(k,filters[k]) for k in filters.keys() ]
        if len(fs)<1:
            f=[]
        else:
            f=fs[0]
            for i in range(1,len(fs)):
                f=And(f,fs[i])
        return db.query(f)

    def update(self,id_,properties):
        if 'status' in properties:
            properties['last_updated']=time.time()
        return db.update(id_,properties)

    def _score(self,task):
        rv=task.priority+1/task.last_updated
        return rv

    def _routine(self):
        tasks=db.query((Equal('status','submitted')))
        print(tasks)
        for t in tasks:
            if (t.life_span>0) and ((time.time()-t.last_updated)>=t.life_span):
                print(12345)
                self.update(t.id,{'status':'failed'})

    def top(self,cnt):
        f1=Equal('status','submitted')
        f2=Equal('status','failed')
        f3=Greater('max_tries',0)
        f=And(Or(f1,f2),f3)
        tasks=db.query(f)
        scores=[ {'id':task.id,'score':self._score(task)} for task in tasks ]
        rvs=heapq.nlargest(cnt,scores,key=lambda s:s['score'])
        return [ db.query(Equal('id',t['id']))[0] for t in rvs]

manager=TaskManager()
