from .skeletonize import Skeletonize

class Engine():
    
    def __init__(self, name, addr, number=1):
        self.name = name
        self.number = number
        self.addr = addr if addr.startswith('http') else 'http://' + addr
        
    def run(self):
        if self.name == 'skeletonize':
            Skeletonize(self.addr, self.number).run()
