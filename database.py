import json
from abc import ABCMeta,abstractmethod
import sqlite3 as sql

class Filter():
    pass


class And(Filter):
    
    __op__='and'

    def __init__(self,a,b):
        self.a=a
        self.b=b


class Or(Filter):
    
    __op__='or'

    def __init__(self,a,b):
        self.a=a
        self.b=b


class Greater(Filter):
    
    __op__='greater'

    def __init__(self,a,b):
        self.a=a
        self.b=b


class Equal(Filter):
    
    __op__='equal'

    def __init__(self,a,b):
        self.a=a
        self.b=b

class Not(Filter):
    
    __op__='not'

    def __init__(self,a):
        self.a=a


class DataBase():
    
    __metaclass__=ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def insert(self,task):
        pass

    @abstractmethod
    def update(self,id_,properties):
        pass

    @abstractmethod
    def query(self,filters):
        pass

    @abstractmethod
    def next_available_id(self):
        pass
        

class SqliteDataBase(DataBase):

    def __init__(self,name):
        super(SqliteDataBase,self).__init__()
        self.name=name
        conn=sql.connect(self.name)
        conn.execute('''
                        CREATE TABLE IF NOT EXISTS task (
                        id int,
                        type text,
                        name text,
                        description text,
                        config text,
                        status text,
                        priority int,
                        life_span real,
                        max_tries int,
                        submitted real,
                        last_updated real,
                        comment text,
                        user text)
                        ''')
        conn.commit()
        conn.close()

    def insert(self,task):
        conn=sql.connect(self.name)
        conn.execute('''INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (task.id,task.type,task.name,task.decription,json.dumps(task.config),task.status,task.priority,
                task.life_span,task.max_tries,task.submitted,task.last_updated,task.comment.task.user))
        conn.commit()
        conn.close()

    def update(self,id_,properties):
        conn=sql.connect(self.name)
        cmd='UPDATE task SET '
        keys=[]
        values=[]
        for k in properties:
            keys.append(k)
            values.append(properties[k])
        for k in keys:
            cmd+=k+'=?,'
        cmd=cmd[:-1]
        conn.execute(cmd,values)
        conn.commit()
        conn.close()

    def query(self,filters):
        cmd='SELECT * from '

    def next_available_id(self):
        conn=sql.connect(self.name)
        conn.execute('SELECT MAX(id) FROM task')
        max_id=conn.fetchone()
        return max_id+1

