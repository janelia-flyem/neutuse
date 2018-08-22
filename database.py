import json
from abc import ABCMeta,abstractmethod
import sqlite3 as sql
from task import Task

class Filter():
    pass


class And(Filter):

    def __init__(self,a,b):
        self.a=a
        self.b=b


class Or(Filter):
    
    def __init__(self,a,b):
        self.a=a
        self.b=b


class Greater(Filter):
    
    def __init__(self,a,b):
        self.a=a
        self.b=b


class Equal(Filter):
    
    def __init__(self,a,b):
        self.a=a
        self.b=b

class Not(Filter):
    
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

    def __init__(self,name,model):
        super(SqliteDataBase,self).__init__()
        self.name=name
        self.model=model
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
        conn=sql.connect(self.name,check_same_thread=False)
        cur=conn.cursor()
        cur.execute('''INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (task.id,task.type,task.name,task.description,json.dumps(task.config),task.status,task.priority,
                task.life_span,task.max_tries,task.submitted,task.last_updated,task.comment,task.user))
        conn.commit()
        conn.close()
        return True

    def update(self,id_,properties):
        conn=sql.connect(self.name,check_same_thread=False)
        cur=conn.cursor()
        cmd='UPDATE task SET '
        keys=[]
        values=[]
        for k in properties:
            keys.append(k)
            values.append(properties[k])
        for k in keys:
            cmd+=k+'=?,'
        cmd=cmd[:-1]
        cmd+=' WHERE id=?'
        values.append(id_)
        cur.execute(cmd,values)
        conn.commit()
        conn.close()
        return True

    def query(self,filters):
        conn=sql.connect(self.name,check_same_thread=False)
        cur=conn.cursor()
        if not filters:
            cmd='SELECT * FROM task'
        else:
            cmd='SELECT * FROM task WHERE '
            cmd+=self._filters2sql(filters)
        print(cmd)
        cur.execute(cmd)
        rv=[]
        for i in cur.fetchall():
            rv.append(self._to_model(i))
        conn.close()
        return rv

    def next_available_id(self):
        conn=sql.connect(self.name,check_same_thread=False)
        cur=conn.cursor()
        cur.execute('SELECT MAX(id) FROM task')
        rv=cur.fetchone()
        if rv[0] is not None:
            max_id=rv[0]
        else:
            max_id=0
        conn.close()
        return max_id+1
    
    def _to_model(self,obj):
        dct={'id':obj[0],'type':obj[1],'name':obj[2],'description':obj[3],
                'config':json.loads(obj[4]),'status':obj[5],'priority':obj[6],
                'life_span':obj[7],'max_tries':obj[8],'submitted':obj[9],
                'last_updated':obj[10],'comment':obj[11]}
        return self.model(**dct)

    def _filters2sql(self,filters):
        if isinstance(filters,And):
            cmd='('+self._filters2sql(filters.a)+') AND ('+self._filters2sql(filters.b)+')'
        elif isinstance(filters,Or):
            cmd='('+self._filters2sql(filters.a)+') OR ('+self._filters2sql(filters.b)+')'
        elif isinstance(filters,Equal):
            cmd=self._filters2sql(filters.a)+' = '
            if isinstance(filters.b,str):
                cmd+="'"
            cmd+=self._filters2sql(filters.b)
            if isinstance(filters.b,str):
                cmd+="'"
        elif isinstance(filters,Greater):
            cmd=self._filters2sql(filters.a)+' > '+self._filters2sql(filters.b)
        elif isinstance(filters,Not):
            cmd=' NOT ('+self._filters2sql(filters.a)+')'
        else :
            cmd=str(filters)
        return cmd

if __name__=='__main__':
    db=SqliteDataBase('test.db',Task)
    db.query(Or(Greater('max_tries',0),Equal('status','processing')))
