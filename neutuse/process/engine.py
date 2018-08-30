from .skeletonize import Skeletonize

class Engine():
    
    def __init__(self, name, addr, log_file='', number=1):
        self.name = name
        self.number = number
        self.log_file = log_file
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        
    def run(self):
        if self.name == 'skeletonize':
            Skeletonize(self.addr, self.log_file, self.number).run()
