import threading
import time
from datetime import datetime, timedelta


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from neutuse.database.models import Base, Task, Service
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
        
    def _del__(self):
        self.session.close()
        
    def all(self):
        return self.session.query(Task).all()
        
    def add(self, task):
        rv = self.session.add(task)
        self.session.commit()
        return rv
        
    def get(self, id_):
        return self.session.query(Task).get(id_)
        
    def update(self, id_or_task, key_values={}):
        if isinstance(id_or_task, Task):
            rv =1
        else:
            rv = self.session.query(Task).filter(Task.id == id_or_service).update(key_values)
        self.session.commit()
        return rv
        
    def delete(self, id_or_task):
        if isinstance(id_or_task, Task):
            rv = self.session.delete(id_or_task)
        else:
            rv = self.session.query(Task).filter(Task.id == id_or_service).delete()
        self.session.commit()
        return rv
    


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
        session.add(service)
        session.commit()
        self.logger.warning('{} has been added to neutuse.'.format(service))
        rv = service.id
        session.close()
        return rv
        
    def get(self, id_):
        session = self.Session()
        rv = session.query(Service).get(id_)
        rv = rv.as_dict()
        session.close()
        return rv
        
    def update(self, id_, key_values={}):
        session = self.Session()
        rv = session.query(Service).filter(Service.id == id_).update(key_values)
        session.commit()
        session.close()
        return rv
        
    def delete(self, id_):
        session = self.Session()
        rv = session.query(Service).filter(Service.id == id_).delete()
        session.commit()
        session.close()
        return rv
    
    def _routine(self):
        session = self.Session()
        expired = session.query(Service).filter(Service.last_active < datetime.now() - timedelta(minutes=1) )
        for e in expired:
            self.logger.warning('{} is down'.format(e))
            session.delete(e)
        session.commit()
        session.close()
        timer = threading.Timer(60, self._routine)
        timer.start()
       

if __name__ == '__main__':
    man = Manager("sqlite:///:memory:")
