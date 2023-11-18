
from main_editor import Window


class EditorCore:

    __editor        : Window

    def start(self):
        self.__editor.show()

    def __init__(self) -> None:
        self.__editor = Window()

if __name__ == "__main__":
    print('Starting Editor...')

    core = EditorCore()
    core.start()

