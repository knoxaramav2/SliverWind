
from collections import namedtuple
from enum import Enum


Color = namedtuple('name', 'value')

class Colors(Enum):

    WHITE   = Color(0, (255, 255, 255))
    BLACK   = Color(1, (255, 255, 255))

    RED     = Color(2, (255, 0, 0))
    GREEN   = Color(3, (0, 255, 0))
    BLUE    = Color(4, (0, 0, 255))

