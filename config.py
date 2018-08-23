from storage.sqlite import Sqlite
from model.task import Task


SERVER='http://127.0.0.1:5000/'
CHECK_INTERVAL=5
db=Sqlite('test.db',Task)
