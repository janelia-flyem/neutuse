from storage.sqlite import Sqlite
from model.task import Task


SERVER='http://127.0.0.1:5000/'
db=Sqlite('test.db',Task)
