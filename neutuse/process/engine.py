from .taskproc import TaskProcessor

class Engine():
    
    '''
    This class is the engine of running different processes.
    '''
    
    def __init__(self, name, config):
        '''
        Args:
            name(str): The name of process to run
            config(dict): Configs passed to process
        '''
        self.name = name
        self.config = config
        
    def run(self):
        '''
        Start running the process
        '''
        for subclass in TaskProcessor.__subclasses__():
            name = subclass.__type_name__[1]
            if name == self.name:
                subclass(self.config).run()
