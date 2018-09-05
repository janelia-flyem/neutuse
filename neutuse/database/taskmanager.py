import time
import threading
import heapq
from .task import Task
from .storage import StorageBase
from .storage.operation import Equal, And, Or, Not, Greater

class TaskManager():
    
    '''
    This class manages tasks and exposes common operating functions such as insert, query and update tasks.
    '''
    
    def __init__(self, db, check_interval=10, waiting_time=5, enable_retry=False):
        assert( isinstance(db, StorageBase) )
        self.db = db
        self.check_interval = check_interval
        self.waiting_time = waiting_time
        self.enable_retry = enable_retry
        self._check_routine()
        self.locks = {}
        
    def insert(self, task):
        assert( isinstance(task,Task) )
        lock = self.locks.setdefault('insert',threading.Lock())
        with lock:
            task.id = self.db.next_available_id()
            return self.db.insert(task)

    def query(self, filters,odered_by='',desc=False):
        fs = [ Equal(k, filters[k]) for k in filters.keys() ]
        if len(fs) < 1:
            f = []
        else:
            f = fs[0]
            for i in range(1, len(fs)):
                f = And(f, fs[i])
        return self.db.query(f,odered_by,desc)

    def update(self, id_, properties):
        if 'status' in properties:
            properties['last_updated'] = time.time()
        return self.db.update(id_, properties)

    def _score(self, task):
        rv = task.priority + 1 / task.last_updated
        return rv

    def _check_routine(self):
        tasks = self.db.query((Equal('status', 'processing')))
        for t in tasks:
            if time.time() - t.last_updated >= t.life_span:
                self.update(t.id, {'status' : 'expired'})
        
        tasks = self.db.query((Equal('status', 'waiting')))
        for t in tasks:
            if time.time() - t.last_updated >= self.waiting_time:
                self.update(t.id, {'status' : 'submitted'})

        timer = threading.Timer(self.check_interval, self._check_routine)
        timer.start()
        
    def top(self, cnt, type_, name):
        '''
        This function query top n tasks based on their priorities
        Args:
            cnt(int): Number of tasks to fetch
            type_(str): The type of tasks
            name(str): The name of tasks
        Returns:
            list: array of top cnt tasks
        '''
        f = Equal('status','submitted')
        if self.enable_retry:
            f = Or(f,Equal('status', 'expired'))
        f = And(f, Greater('max_tries', 0))
        f = And(f, Equal('type', type_))
        f = And(f, Equal('name', name))
        lock = self.locks.setdefault((type_,name),threading.Lock())
        with lock:
            tasks = self.db.query(f)
            scores = [ {'id' : task.id,'score' : self._score(task) } for task in tasks ]
            rvs = heapq.nlargest(cnt, scores,key = lambda s : s['score'])
            tasks = [ self.db.query(Equal('id', t['id']))[0] for t in rvs]
            for t in tasks:
                self.update(t.id, {'status' : 'waiting'})
            return tasks
