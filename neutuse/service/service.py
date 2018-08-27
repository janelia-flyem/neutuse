from .skeletonize import Skeletonize

class Service():
    
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        
    def run(self):
        if self.name == 'skeletonize':
            Skeletonize(self.addr).run()
