
from enum import Enum


RUN_RESULT = Enum(
    'run_results', [
        'OK',
        'EXIT'
    ]
)

class Runnable:

    def run(self) -> RUN_RESULT:pass
    def exit(self):pass


class Serializeable:

    def serialize(self) -> str: pass
    def deserialize(self, raw:str): pass

