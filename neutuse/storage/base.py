from abc import ABCMeta,abstractmethod


class Base():
    
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def insert(self, task):
        pass

    @abstractmethod
    def update(self, id_, properties):
        pass

    @abstractmethod
    def query(self, filters):
        pass

    @abstractmethod
    def next_available_id(self):
        pass

