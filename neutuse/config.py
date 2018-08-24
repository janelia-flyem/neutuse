from storage.sqlite import Sqlite
from model.task import Task


SERVER='http://127.0.0.1:5000/'
CHECK_INTERVAL=1 #seconds
WATING_TIME=60 #seconds
ENABLE_RETRY=False
db=Sqlite('test.db',Task)
