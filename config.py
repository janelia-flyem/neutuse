from storage.sqlite import Sqlite
from model.task import Task

db=Sqlite('test.db',Task)
