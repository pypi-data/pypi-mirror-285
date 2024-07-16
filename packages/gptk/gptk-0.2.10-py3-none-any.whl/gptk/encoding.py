'''Classes to encode and decode text data in various(currently 1) formats.
'''

from auto_all import start_all, end_all
import base64

start_all()

class AsInt:
    '''Static methods to store arbitrary python strings as integer values
        representing base64 encoded text.
    '''
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

    @staticmethod
    def encode(s:str = '', encoding = 'utf-8')->int:
        '''Return an integer which uniquely encodes the given string.
        '''
        msg = base64.urlsafe_b64encode(bytes(s, encoding)).decode().replace('=', '')
        return sum([2**(6*i)*AsInt.alphabet.index(msg[i]) for i in range(len(msg))])
    
    @staticmethod
    def decode(i:int = 86260412497540155604539912989134339022466052582932732307,
               encoding:str = 'utf-8')->str:
        '''Return the string encoded (base64/utf-8) by the given integer.
        '''
        base = 2**6
        txt=[]
        while i > 0:
            c=i%base
            i=i//base
            txt.append(AsInt.alphabet[c])

        while len(txt)%4:
            txt.append('=')
            
        return base64.urlsafe_b64decode(bytes(''.join(txt), encoding)).decode()


end_all()
