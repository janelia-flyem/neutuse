import json
import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, Text, Interval, DateTime
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def as_dict(self):
    rv = {}
    for c in self.__table__.columns:
        k = c.name
        v = getattr(self, k)
        if isinstance(v, datetime.timedelta):
            v = v.seconds
        rv[k] = v 
    return rv


def filters_convertor(model, filters):
    rv = {}
    c = model.__table__.columns
    for k,v in filters.items():
        if type(c[k].type) == Integer:
            rv[k] = int(v)
        elif type(c[k].type) == String:
            rv[k] = str(v)
        elif type(c[k].type) == Text:
            rv[k] = str(v)
        elif type(c[k].type) == Interval:
            rv[k] = datetime.timedelta(seconds = v)
        else:
            rv[k] = v
    return rv


Base.as_dict = as_dict
Base.filters_convertor = filters_convertor


class Json(TypeDecorator):

    impl = Text
    
    def process_bind_param(self, value, dialect):
        return json.dumps(value)
      
    def process_result_value(self, value, dialect):
        return json.loads(value)

class Dict(TypeDecorator):
    
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if not isinstance(value,dict):
            raise TypeError(str(value) + ' is not a dict')
        return json.dumps(value)
      
    def process_result_value(self, value, dialect):
        return json.loads(value)    

    
class List(TypeDecorator):
    
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if not isinstance(value,list):
            raise TypeError(str(value) + ' is not a list')
        return json.dumps(value)
      
    def process_result_value(self, value, dialect):
        return json.loads(value)  
        

class Task(Base):
    
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(128), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    description = Column(Text, default='')
    config = Column(Dict, nullable=False)
    status = Column(String(128), default='submitted')
    priority = Column(Integer, default=0)
    life_span = Column(Interval, default=datetime.timedelta(hours=1))
    max_tries = Column(Integer, default=1)
    submitted = Column(DateTime, default=datetime.datetime.now())
    last_updated = Column(DateTime, default=datetime.datetime.now())
    comments = Column(List, default=[])
    user = Column(String(128), default='anonymous')
    service_id = Column(Integer, ForeignKey('services.id'))

    def __repr__(self):
        return '''<Task(id={}, type={}, name={}, description={}, config={},
                    status={}, priority={}, life_span={}, max_tries={}, submitted={},
                    last_update={}, comments={}, user={}, service_id={})>'''.format(self.id,
                    self.type, self.name, self.description, self.config, self.status, self.priority,
                    self.life_span, self.max_tries, self.submitted, self.last_updated, self.comments,
                    self.user, self.service_id)
        
 
class Service(Base):
    
    __tablename__ = 'services'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(128), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    schema = Column(Dict, default={})
    status = Column(String(128), default='ready')
    last_active = Column(DateTime, default=datetime.datetime.now())
    created = Column(DateTime, default=datetime.datetime.now())
    description = Column(Text, default='')
    mode = Column(String(128), default='pull')
    push_url = Column(String(128), default='')
    tasks = relationship('Task', backref='service')
    
    def __repr__(self):
        return '''<Service(id={}, type={}, name={}, schema={}, status={}, last_active={}, created={}, description={}, mode={}, push_url={}, tasks={})>'''.format(self.id, self.type, self.name, self.schema, self.status, self.last_active, self.created, self.description, self.mode, self.push_url, self.tasks)
    

if __name__ == '__main__':
    pass
    
