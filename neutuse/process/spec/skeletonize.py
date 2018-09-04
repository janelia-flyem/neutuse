import os
import time
import json
import requests as rq
from pyzem.compute import skeletonizer as skl
from pyzem.dvid import dvidenv

from neutuse.process.taskproc import TaskProcessor

class Skeletonize(TaskProcessor):
    
    __schema__ = {
        'input' : {'required': False, 'type': str},
        'dvid' : {'required': False, 'type': dict},
        'force_update' : {'required': False, 'type': bool},
        'bodyid' : {'required' : True, 'type' : int},
        'output' : {'required' : False, 'type' : str}
    }

    __type_name__ = ['dvid', 'skeletonize']
    
        
    def debug(self):
        skeletonizer = skl.Skeletonizer()
        print(skeletonizer._executable)

    def process(self, task):
        skeletonizer = skl.Skeletonizer()
        skeletonizer.setExecutable(self.config.get('command','neutu'))

        # env = dvidenv.DvidEnv()

        config = task['config']
        skeletonizer.configure(config)
        skeletonizer.run()
        if skeletonizer.succeeded:
            self.success(task)
        else:
            self.log(task, 'processing process failed')
            self.fail(task)

        # cmd = 'neutu --command --skeletonize '
        # cmd += config['input']
        # if 'force_update' in config and config['force_update']:
        #     cmd += ' --force '
        # if 'bodyid' in config:
        #     cmd += ' --bodyid '+ str(config['bodyid'])
        # if 'output' in config:
        #     env.load_source(config['output'])
        #     # cmd += ' -o ' + config['output']
        
        # skeletonizer.setDvidEnv(env)
        # skeletonizer.skeletonize(body_id, False, forceUpdate)

        # self.log(task, cmd)
        
        # rv = os.system(cmd)
        
        # if rv == 0:
        #     self.success(task)
        # else:
        #     self.log(task, 'processing process failed')
        #     self.fail(task)
    
if __name__ == '__main__':
    print("debugging...")
    s = Skeletonize(addr='http://127.0.0.1:5000')
    s.debug()
