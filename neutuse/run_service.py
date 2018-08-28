import argparse

from .service import Service


def run_service(name, addr, number=1):
    service = Service(name, addr, number)
    service.run()


if  __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str)
    parser.add_argument('-a', '--addr', type=str, default='127.0.0.1:5000')
    parser.add_argument('-n', '--number', type=int, default=1)
    args=parser.parse_args()
    run_service(args.name, args.addr, args.number)     
