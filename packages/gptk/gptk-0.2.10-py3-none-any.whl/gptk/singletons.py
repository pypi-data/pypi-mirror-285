'''
'''
from sys import getsizeof
from auto_all import start_all, end_all
from abc import ABC, abstractmethod

from base64 import urlsafe_b64encode as b64_encode
try:
    from .encoding import AsInt
except:
    from gptk.encoding import AsInt
start_all()

class Singleton(ABC):
    '''Classic Singleton implementation as an Abstract Base Class. Simply
        subclass Singleton, override init, and implement whatever function-
        ality is required.  The __new__ and __init__ details are already
        handled.
        
        EXAMPLE:
        class Registry(Singleton):
            def init(self, *args, **kwargs):
                self.data = kwargs.get('data', None)
                ...
                
    '''
    
    def __new__(cls, *args, **kwargs):
        '''Return the canonical instance of the class.
        '''
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        '''CAUTION: DANGEROUS OVERRIDE!
            This __init__ contains logic to prevent unintended 
                reinitialization. If overridden, this is ought 
                to be considered.

            :keyword arguments:
                reinit: bool; if true, run self.init() again;
                                otherwise, do nothing.
        '''
        if not hasattr(self, '_initialized'):
            self._initialized = False
        self._initialized = False if bool(kwargs.get('reinit',False)
                                         ) else self._initialized
        if not self._initialized:
            self.init()
            self._initialized = True
        
    @abstractmethod
    def init(self, *args, **kwargs):
        '''Implement this method as a stand-in for __init__, who is "quite pre-
            occupied at the moment, thank you very much."
        '''


end_all()
