import time
import heapq
import threading
from config import db
from database import And,Or,Not,Equal,Greater

class TaskManager():

    def __init__(self):
        timer=threading.Timer(60,self._routine,[self])
        timer.start()

    def insert(self,task):
        task.id=db.next_available_id()
        return db.insert(task)

    def query(self,filters):
        if isinstance(filters,dict):
            fs=[ Equal(k,filters[k] for k in filters.keys()) ]
            if len(fs)<1:
                return []
            if len(fs)==1:
                f=fs[0]
            else:
                f=fs[0]
                for i in range(1,len(fs)):
                    f=And(f,fs[i])
        else:
            f=filters
        return db.query(filters)

    def update(self,id_,properties):
        if 'status' in properties:
            properties['last_updated']=time.time()
        return db.update(id_,properties)

    def score(self,task):
        return 0.0

    def _routine(self):
        tasks=db.query(Equal('status','processing'))
        for t in tasks:
            if time.time()-t.last_updated>=t.life_span:
                self.update(t.id,{'status':'failed'})

    def top(self,cnt):
        f1=Equal('status','submitted')
        f2=Equal('status','failed')
        f3=Greater('max_tries',0)
        f=And(Or(f1,f2),f3)
        tasks=db.query(f)
        scores=[ {'id':task.id,'score':self.score(task)} for task in tasks ]
        return [ self.query(Equal('id',t['id']) for t in heapq.nlargest(cnt,scores,key=lambda s:s['score'])) ]

manager=TaskManager()
