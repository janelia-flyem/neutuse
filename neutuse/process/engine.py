from .skeletonize import Skeletonize

class Engine():
    
    '''
    This class is the engine of running different processes.
    '''
    
    def __init__(self, name, addr, log_file='', num_workers=1):
        '''
        Args:
            name(str): The name of process to run
            addr(str): The address database if running
            log_file(str): Name of file to write logs
            num_workers(int): Maximum number of workers the process to keep 
        '''
        self.name = name
        self.num_workers = num_workers
        self.log_file = log_file
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        
    def run(self):
        '''
        Start running the process
        '''
        if self.name == 'skeletonize':
            Skeletonize(self.addr, self.log_file, self.num_workers).run()
