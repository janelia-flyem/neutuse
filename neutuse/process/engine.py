from .taskproc import TaskProcessor

class Engine():
    
    '''
    This class is the engine of running different processes.
    '''
    
    def __init__(self, names, config):
        '''
        Args:
            name(str): The name of process to run
            config(dict): Configs passed to process
        '''
        self.names = names
        self.config = config
        
    def run(self):
        '''
        Start running the process
        '''
        for name in self.names:
            for subclass in TaskProcessor.__subclasses__():
                name2 = subclass.__type_name__[1]
                if name == name2:
                    subclass(self.config).run()
