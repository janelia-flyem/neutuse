from abc import ABCMeta,abstractmethod


class StorageBase():
    
    '''
    This is the base class of storage layer.
    Subclasses should implement insert, update, query and next_available_id functions.
    next_available_id should returns a unique id for task.
    '''
    
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
    def query(self, filters,odered_by='',desc=False):
        pass

    @abstractmethod
    def next_available_id(self):
        pass

