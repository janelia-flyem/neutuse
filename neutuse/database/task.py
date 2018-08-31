import os
import sys
import time


class Task(dict):

    '''
    This class defines the task schema.
    '''
    
    __status__ = ('submitted', 'waiting', 'processing', 'expired', 'failed', 'done')
    __mapping__ = {
        'id' : {'type' : int, 'required' : False, 'default' : 0},
        'type' : {'type' : str, 'required' : False, 'default' : 'dvid'},
        'name' : {'type' : str, 'required' : True},
        'description' : {'type' : str, 'required' : False, 'default' : '---'},
        'config' : {'type' : dict, 'required' : True},
        'status' : {'type' : str, 'required' : False, 'default' : 'submitted'},
        'priority' : {'type' : int, 'required' : False, 'default' : 0},
        'life_span' : {'type' : int, 'required' : False, 'default' : 3600},
        'max_tries' : {'type' : int, 'required' : False, 'default' : 1},
        'submitted' : {'type' : float, 'required' : False, 'default' : lambda : time.time()},
        'last_updated' : {'type' : float, 'required' : False, 'default' : lambda:time.time()},
        'comments' : {'type' : list, 'required' : False, 'default' : []},
        'user' : {'type' : str, 'required' : False, 'default' : 'anonymous'}
    }

    def __init__(self, **kwargs):
        for k in kwargs:
            if k not in self.__mapping__.keys():
                raise AttributeError('class Task does not have attribute ' + str(k))
        for k in self.__mapping__:
            if self.__mapping__[k]['required']:
                if not k in kwargs:
                    raise Exception(str(k) + ' should be provided')
                if not isinstance(kwargs[k],self.__mapping__[k]['type']):
                    raise Exception('type of {} should be {}, but you provide {} with value {}'.format(str(k),
                        self.__mapping__[k]['type'],type(kwargs[k]),kwargs[k]))
                self[k] = kwargs[k]
            else:
                if k in kwargs:
                    if not isinstance(kwargs[k],self.__mapping__[k]['type']):
                        raise Exception('type of {} should be {}, but you provide {} with value {}'.format(str(k),
                        self.__mapping__[k]['type'],type(kwargs[k]),kwargs[k]))
                    self[k] = kwargs[k]
                else:
                    try:
                        self[k] = self.__mapping__[k]['default']()
                    except:
                        self[k] = self.__mapping__[k]['default']
        
    def __getattr__(self, name):
        if name in self and name in self.__mapping__:
                return self[name]
        raise AttributeError('class Task does not have attribute ' + str(name))

    def __setattr__(self, name, value):
        if name in self.__mapping__:
            if isinstance(value, self.__mapping__[name]['type']):
                return super(Task, self).__setitem__(name, value)
            raise TypeError(str(name) + ' should be type ' + str(self.__mapping__[name]['type']))
        raise AttributeError('class Task does not have attribute ' + str(name))

