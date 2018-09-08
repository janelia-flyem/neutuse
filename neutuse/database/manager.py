import threading
import time
from datetime import datetime, timedelta


from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from neutuse.database.models import Base, Task, Service, filters_convertor
from neutuse.database.utils.logger import Logger


class Manager():
    
    instance = None
    
    @classmethod
    def set(cls, **kwargs):
        cls.instance = Manager(**kwargs)
        
    @classmethod
    def get(cls):
        if cls.instance is None:
            raise AttributeError('Manager instance has not been created')
        return cls.instance
        
    def __init__(self, **kwargs):
        backend = kwargs.get('backend', 'sqlite:///test.db')
        self._init_backend(backend)
        
        logfile = kwargs.get('logfile', None)
        email = kwargs.get('email', None)
        slack = kwargs.get('slack', None)
        self._init_logger(logfile, email, slack)
        
        self._init_sub_managers()

    def _init_logger(self, logfile, email, slack):
        self._logger = Logger(logfile, email, slack)
        
    def _init_backend(self, backend):
        self.engine = create_engine(backend)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _init_sub_managers(self):
        self._task_manager = TaskManager(self)
        self._service_manager = ServiceManager(self)
        
    @property
    def task(self):
        return self._task_manager
        
    @property
    def service(self):
        return self._service_manager

    @property
    def logger(self):
        return self._logger


class TaskManager():
    
    def __init__(self, man):
        self.Session = man.Session
        self.logger = man.logger
        self._routine()
        
    def all(self):
        session = self.Session()
        rv = session.query(Task).all()
        rv = [ s.as_dict() for s in rv ]
        session.close()
        return rv
        
    def add(self, task):
        session = self.Session()
        if 'life_span' in task :
            task['life_span'] = timedelta(seconds = task['life_span'])
        task = Task(**task)
        try:
            session.add(task)
            session.commit()
            rv = task.id
            return rv
        except:
            session.rollback()
        finally: 
            session.close()
        
        
    def get(self, id_):
        session = self.Session()
        rv = session.query(Task).get(id_)
        if rv:
            rv = rv.as_dict()
        session.close()
        return rv
        
    def update(self, id_, key_values={}):
        session = self.Session()
        try:
            rv = session.query(Task).filter(Task.id == id_).update(key_values)
            session.commit()
            return rv
        except:
            session.rollback()
        finally:
            session.close()
        
    def delete(self, id_):
        session = self.Session()
        try:
            rv = session.query(Task).filter(Task.id == id_).delete()
            session.commit()
            return rv
        except:
            session.rollback()
        finally: 
            session.close()
        
    
    def top(self, type_, name, k):
        session = self.Session()
        
        rv = session.query(Task).filter((Task.status == 'submitted') | (Task.status == 'expired'))\
        .filter(Task.max_tries > 0)\
        .filter((Task.type == type_) & (Task.name == name))\
        .order_by(Task.priority.desc())\
        .order_by(Task.last_updated)\
        .limit(k)
        
        for r in rv:
            rv.status = 'waiting'
        rv = [ s.as_dict() for s in rv ]
        session.commit()
        session.close()
        return rv
    
    def add_comment(self, id_, comment):
        session = self.Session()
        task = session.query(Task).get(id_)
        if task:
            comments = task.comments
            comments.append(comment)
            try:
                rv = session.query(Task).filter(Task.id == id_).update({'comments': comments})
                session.commit()
                return rv
            except:
                session.rollback()
            finally:
                session.close()
        else:
            raise Exception('No task has this ID')

        
        
    def query(self, filters):
        session = self.Session()
        rv =  session.query(Task)
        #filters = filters_convertor(Task, filters)
        if len(filters) == 0:
           rv = rv.all()
        else:
            for k,v in filters.items():
                rv = rv.filter(getattr(Task,k) == v)
                #print(str(rv))
        rv = [ s.as_dict() for s in rv]
        session.close()
        return rv
            
    def pagination(self, filters, order_by, page_size, page_index, desc_=False):
        session = self.Session()
        if desc_:
            rv = session.query(Task).order_by(desc(order_by))
        else:
            rv = session.query(Task).order_by(order_by)
        filters = list(filters.items())
        if len(filters) == 0:
            rv = rv.all()
        for f in filters:
            k,v = f
            rv = rv.filter(k == v)
        rv = rv[page_size * page_index : page_size * (page_index + 1)]
        rv = [ s.as_dict() for s in rv]
        session.close()
        return rv
        
        
    def _routine(self):
        session = self.Session()
        
        session.query(Task).filter(Task.status == 'processing')\
        .filter(Task.last_updated < datetime.now() - Task.life_span ).update({'status': 'expired'})
        
        session.query(Task).filter(Task.status == 'wating')\
        .filter(Task.last_updated + timedelta(minutes=1) < datetime.now() ).update({'status': 'submitted'})
        
        session.commit()
        session.close()
        timer = threading.Timer(60, self._routine)
        timer.start()
        
        

class ServiceManager():
    
    def __init__(self, man):
        self.Session = man.Session
        self.logger = man.logger
        self._routine()
        
    def all(self):
        session = self.Session()
        rv = session.query(Service).all()
        rv = [ s.as_dict() for s in rv ]
        session.close()
        return rv
        
    def add(self, service):
        session = self.Session()
        service = Service(**service)
        try:
            session.add(service)
            session.commit()
            self.logger.warning('{} has been added to neutuse.'.format(service))
            rv = service.id
            return rv
        except:
            session.rollback()
        finally:
            session.close()
        
    def get(self, id_):
        session = self.Session()
        rv = session.query(Service).get(id_)
        rv = rv.as_dict()
        session.close()
        return rv
        
    def update(self, id_, key_values={}):
        session = self.Session()
        try:
            rv = session.query(Service).filter(Service.id == id_).update(key_values)
            session.commit()
            return rv
        except:
            session.rollback()
        finally:
            session.close()
        
        
    def delete(self, id_):
        session = self.Session()
        try:
            rv = session.query(Service).filter(Service.id == id_).delete()
            session.commit()
            return rv
        except:
            session.rollback()
        finally:
            session.close()
        
    
    def _routine(self):
        session = self.Session()
        expired = session.query(Service).filter(Service.last_active < datetime.now() - timedelta(minutes=3) )
        for e in expired:
            self.logger.warning('{} is down'.format(e))
            session.delete(e)
        session.commit()
        session.close()
        timer = threading.Timer(60, self._routine)
        timer.start()
       

if __name__ == '__main__':
    man = Manager("sqlite:///:memory:")
