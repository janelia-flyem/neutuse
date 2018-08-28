import argparse

from .taskman import TaskMan


def run_taskman(addr, backend, debug=False):
    taskman = TaskMan(addr, backend, debug)
    taskman.run()

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
    parser.add_argument('-d','--debug', action='store_true', default=False)
    parser.add_argument('-b','--backend', default='sqlite:db.db')
    args=parser.parse_args()
    run_taskman(args.addr, args.backend, args.debug)
