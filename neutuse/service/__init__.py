from .skeletonize import Skeletonize 

def run_service(name,host,port):
    if name == 'skeletonize':
        Skeletonize(host,port).run()
    else:
        print(name+' service has not been supported yet')
    
