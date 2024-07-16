'''Enumerations of various natural and constructed phenomena.
'''
from enum import Enum

from auto_all import start_all, end_all, public

start_all()

class Priority(Enum):
    '''A simple priority enumeration for general classification.
    
    Priorities run from 0 to 7 because 8 bins of stuff-to-do is
    plenty.
    
    '''
    NONE = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = MID = 3
    HIGH = 4
    VERY_HIGH = 5
    URGENT = 6
    IMMEDIATE =7



class Planets(Enum):
    '''The EIGHT planets in the Solar system.
    '''
    
    MERCURY = 1
    VENUS = 2 
    EARTH = 3
    MARS = 4
    JUPITER = 5
    SATURN = 6
    URANUS = 7
    NEPTUNE = 8

    

end_all()
