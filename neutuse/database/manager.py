import threading
import time
from datetime import datetime, timedelta
import logging
import logging.handlers
from logging import Handler


from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from neutuse.database.models import Base, Task, Service, HistoryTask
from neutuse.database.utils import mail, slack


class EmailHandler(Handler):
    
    def __init__(self, email):
        self.email = email
        super(EmailHandler,self).__init__()
    
    def emit(self, record):
        entry = self.format(record)
        if self.email:
            email = self.email
            host = email['host']
            user = email['user']
            passwd = email['passwd']
            port = email['port'] if 'port' in email else 25
            sender = mail.MailSender(host,user,passwd,port)
            for to in email['to']:
                sender.add_receiver(to)
            sender.set_subject('neutuse message')
            sender.add_text(entry)
            try:
                sender.send()
            except:
                pass  

    
class SlackHandler(Handler):
    def __init__(self, slack):
        self.slack = slack
        super(SlackHandler,self).__init__()
        
    def emit(self, record):
        entry = self.format(record)
        if self.slack:
            token_file = self.slack['token_file']
            channel = self.slack['channel']
            slack.Slack('neutuse',token_file).send(channel, entry)


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
        
        self.enable_retry = kwargs.get('enable_retry', False)
        self._init_sub_managers()

    def _init_logger(self, logfile, email, slack):
        self._logger = logging.getLogger('neutuse')
        self._logger.setLevel(logging.INFO)        
        logging.getLogger('werkzeug').disabled = True          
        fmt = "%(asctime)-15s %(levelname)s %(filename)s.%(lineno)d %(threadName)s>>>> %(message)s"
   
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(fmt))
        self._logger.addHandler(sh)
        
        if logfile:
            fh = logging.handlers.RotatingFileHandler(logfile,maxBytes = 1024*1024*100, backupCount = 3)    
            fh.setFormatter(logging.Formatter(fmt))
            self._logger.addHandler(fh)
        
        eh = EmailHandler(email)
        eh.setFormatter(logging.Formatter(fmt))
        eh.setLevel(logging.WARNING)  
        self._logger.addHandler(eh)
        
        slh = SlackHandler(slack)
        slh.setFormatter(logging.Formatter(fmt))
        slh.setLevel(logging.WARNING)  
        self._logger.addHandler(slh)

        
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
        self.man = man
        self.Session = man.Session
        self.logger = man.logger
        self.enable_retry = man.enable_retry
        self.locks = {}
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
        except Exception as e:
            self.logger.info(e)
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
        lock = self.locks.setdefault((type_,name),threading.Lock())
        with lock:
            if self.enable_retry:
                tasks = session.query(Task).filter((Task.status == 'submitted') | (Task.status == 'expired'))
            else:
                tasks = session.query(Task).filter(Task.status == 'submitted')
            tasks = tasks.filter(Task.max_tries > 0)\
            .filter((Task.type == type_) & (Task.name == name))\
            .order_by(Task.priority.desc())\
            .order_by(Task.last_updated)\
            .limit(k)
            rv = []
            for r in tasks:
                session.query(Task).filter(Task.id == r.id).update({'status':'waiting'})
                rv.append(r.as_dict())
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

        
    def _query(self, table, filters, order_by=None, start_index=0, end_index=None, desc_=False):
        session = self.Session()
        rv =  session.query(table)
        
        if order_by:
            if desc_:
                rv = rv.order_by(desc(order_by))
            else:
                rv = rv.order_by(order_by)
        
        if len(filters) == 0:
           rv = rv.all()
        else:
            for k,v in filters.items():
                rv = rv.filter(getattr(table,k) == v)
        rv = rv[start_index: end_index]
        rv = [s.as_dict() for s in rv]
        session.close()
        return rv
        
    def query(self, filters, order_by=None, start_index=0, end_index=None, desc_=False):
        if 'status' in filters and filters['status'] == 'history':
            new_filters = {}
            for k,v in filters.items():
                new_filters[k] = v
            new_filters.pop('status')
            return self._query(HistoryTask, new_filters, order_by, start_index, end_index, desc_)
        return self._query(Task, filters, order_by, start_index, end_index, desc_)                
        
    def _routine(self):
        try:
            session = self.Session()
            
            for t in session.query(Task).filter(Task.status == 'processing'):
                if t.last_updated < (datetime.now() - t.life_span):
                    t.status = 'expired'
            session.query(Task).filter(Task.status == 'waiting')\
            .filter(Task.last_updated  < (datetime.now() - timedelta(minutes=1))).update({'status': 'submitted'})
            
            tasks = session.query(Task).filter(Task.status == 'done')\
            .filter(Task.last_updated < (datetime.now() - timedelta(days=1)))
            
            for t in tasks:
                history_task = t.as_dict()
                history_task.pop('id')
                history_task['life_span'] = timedelta(seconds = history_task['life_span'])
                history_task = HistoryTask(**history_task)
                session.add(history_task)
                session.delete(t)
        except Exception as e:
            self.man.logger.warning(e)
            session.rollback()
        finally:
            session.commit()
            session.close()
            timer = threading.Timer(20, self._routine)
            timer.start()
        
        

class ServiceManager():
    
    def __init__(self, man):
        self.man = man
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
        
    def online_services(self):
        session =self.Session()
        
        rv = session.query(Service).filter( (Service.status == 'ready') |  (Service.status == 'busy') )
        rv = [s.as_dict() for s in rv ]
        
        session.close()
        return rv
        
    def _routine(self):
        try:
            session = self.Session()
            expired = session.query(Service).filter(Service.status != 'down')\
            .filter(Service.last_active < (datetime.now() - timedelta(minutes=3)))
            for e in expired:
                self.logger.warning('{} is down'.format(e))
                session.query(Service).filter(Service.id == e.id).update({'status':'down'})
                for t in session.query(Task).filter( (Task.service_id == e.id) & (Task.status == 'processing') ):
                    t.status = 'expired'
                    comments = t.comments
                    comments.append('Expired because service is down')
                    session.query(Task).filter(Task.id == t.id).update({'comments':comments})
        except Exception as e:
            self.logger.warning(e)
        finally:
            session.commit()
            session.close()
            timer = threading.Timer(20, self._routine)
            timer.start()
       

if __name__ == '__main__':
    man = Manager("sqlite:///:memory:")
