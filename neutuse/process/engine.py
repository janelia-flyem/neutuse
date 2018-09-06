from .taskproc import TaskProcessor

class Engine():
    
    '''
    This class is the engine of running different processes.
    '''
    
    def __init__(self, services):
        '''
        Args:
            services(array): Array of services want to run,example (('name1',config1),('name2',config2),(...))
        '''
        self.services= services
        
    def run(self):
        '''
        Start running the process
        '''
        #print(TaskProcessor.__subclasses__())
        for service in self.services:
            name, config = service
            for subclass in TaskProcessor.__subclasses__():
                name2 = subclass.__type_name__[1]
                if name == name2:
                    subclass(config).run()
