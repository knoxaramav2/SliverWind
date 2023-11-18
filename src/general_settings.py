

from enum import Enum

Difficulty = Enum(
    'Difficulty',[
        
        'Peaceful',
        'Easy',
        'Normal',
        'Hard',
        'Deadly'
    ]
)

class GeneralSettings:

    __difficulty        : Difficulty = Difficulty.Normal

    def __init__(self):
        pass

__inst__: GeneralSettings = None

def GetInst():
    global __inst__
    if __inst__ == None:
        __inst__ = GeneralSettings()
    return __inst__