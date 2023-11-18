
import visual_settings
import general_settings
import audio_settings
from audio_settings import AudioSettings
from general_settings import GeneralSettings
from visual_settings import VisualSettings


class GameSettings:

    __visual        : VisualSettings
    __audio         : AudioSettings
    __general       : GeneralSettings

    def __init__(self):
        self.__visual = visual_settings.GetInst()
        self.__audio = audio_settings.GetInst()
        self.__general = general_settings.GetInst()


__inst__: GameSettings = None

def GetInst():
    global __inst__
    if __inst__ == None:
        __inst__ = GameSettings()
    return __inst__

