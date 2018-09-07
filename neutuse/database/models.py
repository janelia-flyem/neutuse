import json
import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, Text, Interval, DateTime
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def as_dict(self):
    return {c.name:getattr(self, c.name) for c in self.__table__.columns}


Base.as_dict = as_dict


class Json(TypeDecorator):

    impl = Text
    
    def process_bind_param(self, value, dialect):
        return json.dumps(value)
      
    def process_result_value(self, value, dialect):
        return json.loads(value)


class Task(Base):
    
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(128), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    description = Column(Text, default='')
    config = Column(Json, nullable=False)
    status = Column(String(128), default='submitted')
    priority = Column(Integer, default=0)
    life_span = Column(Interval, default=3600)
    max_tries = Column(Integer, default=1)
    submitted = Column(DateTime, default=datetime.datetime.now())
    last_update = Column(DateTime, default=datetime.datetime.now())
    comments = Column(Json, default=[])
    user = Column(String(128), default='anonymous')
    service_id = Column(Integer, ForeignKey('services.id'))

    def __repr__(self):
        return '''<Task(id={}, type={}, name={}, description={}, config={},
                    status={}, priority={}, life_span={}, max_tries={}, submitted={},
                    last_update={}, comments={}, user={}, service_id={})>'''.format(self.id,
                    self.type, self.name, self.description, self.config, self.status, self.priority,
                    self.life_span, self.max_tries, self.submitted, self.last_update, self.comments,
                    self.user, self.service_id)
        
 
class Service(Base):
    
    __tablename__ = 'services'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(128), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)
    schema = Column(Json, default={})
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
    
