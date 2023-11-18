

class AudioSettings:

    __level             : float = 50.0
    __mute              : bool = False


    def __init__(self):
        pass



__inst__: AudioSettings = None

def GetInst():
    global __inst__
    if __inst__ == None:
        __inst__ = AudioSettings()
    return __inst__

