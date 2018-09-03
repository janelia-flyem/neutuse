from .skeletonize import Skeletonize

class Engine():
    
    '''
    This class is the engine of running different processes.
    '''
    
    def __init__(self, name, addr, config):
        '''
        Args:
            name(str): The name of process to run
            addr(str): Address that the database is running
            config(dict): Configs passed to process
        '''
        self.name = name
        self.config = config
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        
    def run(self):
        '''
        Start running the process
        '''
        if self.name == 'skeletonize':
            Skeletonize(self.addr, self.config).run()
