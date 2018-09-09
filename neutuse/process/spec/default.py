import os
from neutuse.process.taskproc import TaskProcessor


class Default(TaskProcessor):

    __schema__ = {
        'cmd': {'required': True, 'type': str.__name__},
        'success_code': {'required' : False, 'type': int.__name__}
    }
    
    __type_name__ = ('default', 'default')
    
    def process(self, task):
        config = task['config']
        rv = os.system(config['cmd'])
        success_code = config['success_code'] if 'success_code' in config else 0
        
        if rv == success_code:
            self.success(task)
        else:
            self.fail(task)
    
