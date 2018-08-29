import os
import time
import json
import requests as rq
from .base import Base

class Skeletonize(Base):
    
    __schema__ = {
    'input' : {'required': True, 'type': str},
    'force_update' : {'required': False, 'type': bool},
    'bodyid' : {'required' : False, 'type' : int},
    'output' : {'required' : False, 'type' : str}
    }
    
    def __init__(self, addr, cnt=1):
        super(Skeletonize, self).__init__(addr, 'dvid', 'skeletonize', cnt)
        
    def process(self, task):
        config = task['config']
        cmd = 'neutu --command --skeletonize '
        cmd += config['input']
        if 'force_update' in config and config['force_update']:
            cmd += ' --force '
        if 'bodyid' in config:
            cmd += ' --bodyid '+ str(config['bodyid'])
        if 'output' in config:
            cmd += ' -o ' + config['output']
        
        self.log(task, cmd)
        
        rv = os.system(cmd)
        
        if rv == 0:
            self.success(task)
        else:
            self.log(task, 'processing process failed')
            self.fail(task)
