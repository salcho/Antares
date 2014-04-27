'''
Created on Apr 7, 2014

@author: user
'''

class Singleton(type):
    '''
    Singleton interface
    '''

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance
        
        