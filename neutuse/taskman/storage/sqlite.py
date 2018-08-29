import json
import sqlite3 as sql

from .base import Base
from .op import *

class Sqlite(Base):

    def __init__(self, name, model):
        super(Sqlite, self).__init__()
        self.name = name
        self.model = model
        conn = sql.connect(self.name)
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

    def insert(self, task):
        try:
            conn = sql.connect(self.name)
            cur = conn.cursor()
            cur.execute('''INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (task.id, task.type, task.name, task.description,
                    json.dumps(task.config), task.status,task.priority,
                    task.life_span, task.max_tries, task.submitted, 
                    task.last_updated, json.dumps(task.comment), task.user))
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)
            return False
        return True

    def update(self, id_, properties):
        try:
            if 'id' in properties:
                return False
            conn = sql.connect(self.name)
            cur = conn.cursor()
            cmd = 'UPDATE task SET '
            keys = []
            values = []
            for k in properties:
                keys.append(k)
                values.append(properties[k])
            for k in keys:
                cmd += k + '=?,'
            cmd = cmd[:-1]
            cmd += ' WHERE id=?'
            values.append(id_)
            cur.execute(cmd, values)
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)
            return False
        return True

    def query(self,filters):
        try:
            conn = sql.connect(self.name)
            cur = conn.cursor()
            if not filters:
                cmd = 'SELECT * FROM task'
            else:
                cmd = 'SELECT * FROM task WHERE '
                cmd += self._filters2sql(filters)
            cur.execute(cmd)
            rv = []
            for i in cur.fetchall():
                rv.append(self._to_model(i))
            conn.close()
            return rv
        except Exception as e:
            print(e)
            return []

    def next_available_id(self):
        conn = sql.connect(self.name)
        cur = conn.cursor()
        cur.execute('SELECT MAX(id) FROM task')
        rv = cur.fetchone()
        if rv[0] is not None:
            max_id = rv[0]
        else:
            max_id = 0
        conn.close()
        return max_id + 1
    
    def _to_model(self, obj):
        dct = {'id' : obj[0], 'type' : obj[1], 'name' : obj[2],
                'description' : obj[3], 'config' : json.loads(obj[4]),
                'status' : obj[5], 'priority' : obj[6], 'life_span' : obj[7],
                'max_tries' : obj[8], 'submitted' : obj[9],
                'last_updated' : obj[10], 'comment' : json.loads(obj[11])}
        return self.model(**dct)

    def _filters2sql(self, filters):
        if isinstance(filters,And):
            cmd = '(' + self._filters2sql(filters.a) + ') AND (' + self._filters2sql(filters.b) + ')'
        elif isinstance(filters, Or):
            cmd = '(' + self._filters2sql(filters.a) + ') OR (' + self._filters2sql(filters.b) + ')'
        elif isinstance(filters,Equal):
            cmd = self._filters2sql(filters.a) + ' = '
            if isinstance(filters.b, str):
                cmd += "'"
            cmd += self._filters2sql(filters.b)
            if isinstance(filters.b, str):
                cmd += "'"
        elif isinstance(filters, Greater):
            cmd = self._filters2sql(filters.a) + ' > ' + self._filters2sql(filters.b)
        elif isinstance(filters, Not):
            cmd = ' NOT (' + self._filters2sql(filters.a) + ')'
        else :
            cmd = str(filters)
        return cmd
