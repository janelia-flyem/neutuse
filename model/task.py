import os
import sys
import time


class Task(dict):

    __status__=('submitted','processing','failed','done')
    __mapping__={
        'id':{'type':int,'required':False,'default':0},
        'type':{'type':str,'required':False,'default':'dvid'},
        'name':{'type':str,'required':True},
        'description':{'type':str,'required':False,'default':''},
        'config':{'type':dict,'required':True},
        'status':{'type':str,'required':False,'default':'submitted'},
        'priority':{'type':int,'required':False,'default':0},
        'life_span':{'type':float,'required':False,'default':-1},
        'max_tries':{'type':int,'required':False,'default':1},
        'submitted':{'type':float,'required':False,'default':lambda:time.time()},
        'last_updated':{'type':float,'required':False,'default':lambda:time.time()},
        'comment':{'type':str,'required':False,'default':''},
        'user':{'type':str,'required':False,'default':'anonymous'}
    }

    def __init__(self,**kwargs):
        for k in self.__mapping__:
            if self.__mapping__[k]['required']:
                if not k in kwargs:
                    raise Exception(str(k)+' should be provied')
                self[k]=kwargs[k]
            else:
                if k in kwargs:
                    self[k]=kwargs[k]
                else:
                    try:
                        self[k]=self.__mapping__[k]['default']()
                    except:
                        self[k]=self.__mapping__[k]['default']
        
    def __getattr__(self,name):
        if name in self and name in self.__mapping__:
                return self[name]
        raise AttributeError('class Task does not have attribute '+str(name))

    def __setattr__(self,name,value):
        if name in self.__mapping__:
            if isinstance(value,self.__mapping__[name]['type']):
                return super(Task,self).__setitem__(name,value)
            raise TypeError(str(name)+' should be type '+str(self.__mapping__[name]['type']))
        raise AttributeError('class Task does not have attribute '+str(name))

