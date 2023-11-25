
class Control:

    _name           : str = ''    

    def show(): pass
    def hide(): pass
    def destroy(): pass
    def move():pass

    def __init__(self) -> None:
        pass

class Menu(Control):

    _title          : str = ''

    def __init__(self, title:str) -> None:
        super().__init__()

        self._title = title


class DevTerminal(Control):


    def execute(self):

        return

    def __init__(self):
        super().__init__()