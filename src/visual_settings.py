
class VisualSettings:

    __w             : int = 1280
    __h             : int = 720

    __full_screen   : bool = False

    def full_screen(self):
        
        self._full_screen = not self._full_screen

    def __load_file(self):
        pass

    def size(self)->tuple[int, int]:
        return (self.__w, self.__h)

    def __init__(self):
        self.__load_file()


__inst__: VisualSettings = None

def GetInst() -> VisualSettings:
    global __inst__
    if __inst__ == None:
        __inst__ = VisualSettings()
    return __inst__

