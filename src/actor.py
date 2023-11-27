

from enum import Enum
from pygame import Surface

from asset_manager import AssetManager, AssetUtil, get_assetmanager, get_assetutil
from util import GetUtil

ANIM_STATE = Enum(
    'anime_state',[
        'FRONT_IDLE',
        'SIDE_IDLE',
        'BACK_IDLE',
        
        'FRONT_WALK',
        'SIDE_WALK',
        'BACK_WALK',

        'FRONT_RUN',
        'SIDE_RUN',
        'BACK_RUN',

        'FRON_JUMP',
        'SIDE_JUMP',
        'BACK_JUMP'
    ]
)

class SpriteAnimation:

    __sprite_sheets : dict
    __sprites       : [Surface]
    __frame         : int
    __length        : int
    __state         : ANIM_STATE
    __no_img        : any
    __skip_cnt      : int

    def update(self) -> Surface:

        self.__skip_cnt += 1
        if self.__skip_cnt == 5:
            self.__frame += 1
            self.__skip_cnt = 0

        if self.__length == 0:
            return self.__no_img

        if self.__frame == self.__length:
            self.__frame = 0
        return self.__sprites[self.__frame]

    def set_mode(self, state:ANIM_STATE):
        self.__state = state
        if len(self.__sprite_sheets) == 0:
            return
        dir, act = state.name.lower().split('_')

        #check fallbacks
        while act not in self.__sprite_sheets:
            if act == 'jump': act = 'run'
            elif act == 'run': act = 'walk'
            elif act == 'walk': act = 'idle'
            else: 
                return

        while dir not in self.__sprite_sheets[act]:
            if dir == 'front': dir = 'side'
            elif dir == 'side': dir = 'back'
            elif dir == 'back': dir = 'top'
            elif dir == 'top': dir = 'bottom'
            else:
                return

        self.__sprites = self.__sprite_sheets[act][dir]
        self.__length = len(self.__sprites)
        if self.__frame >= self.__length:
            self.__frame = 0

    def add_spritesheet(self, action:str, dir:str, ss:list[Surface]):
        if ss == None or len(ss) == 0: return
        
        if action not in self.__sprite_sheets:
            self.__sprite_sheets[action] = {}
        
        self.__sprite_sheets[action][dir] = ss

    def __init__(self):
        self.__sprite_sheets = {}
        self.__sprites = []
        self.__state = ANIM_STATE.FRONT_IDLE
        self.__length = 0
        self.__frame = 0
        self.__no_img = GetUtil().missing_img()
        self.__skip_cnt = 0
        

ACTOR_CLASS = Enum(
    'actor_class', [
        'NPC', 'ENEMY', 'PLAYER', 'SUPPORT'
    ]
)


class Actor:

    name        : str = ''
    speed       : float = 1.0
    pos         : tuple[float, float]
    sprite      : Surface

    health      : float = 10.0
    max_health  : float = 10.0
    immortal    : float = False

    __last_pos  : tuple[float, float]

    __animation : SpriteAnimation

    def add_spritesheet(self, action:str, dir:str, ss:list[Surface]):
        self.__animation.add_spritesheet(action, dir, ss)

    def set_sprite_mode(self, mode:ANIM_STATE):
        self.__animation.set_mode(mode)

    def move(self, x:int, y:int):
        self.__last_pos = self.pos
        nx = self.pos[0] + (x*self.speed)
        ny = self.pos[1] + (y*self.speed)
        self.pos = (nx, ny)

    def update(self):
        self.sprite = self.__animation.update()

    def __init__(self, pos:tuple[float, float]):
        self.pos = pos
        self.__animation = SpriteAnimation()
        self.__animation.set_mode(ANIM_STATE.FRONT_IDLE)


class ActorFactory:

    __actor_state       : dict
    __ast_util          : AssetUtil

    def Create(self,
               atype:ACTOR_CLASS,
               store:bool,
               name: str,
               pos:tuple[float, float]
               ) -> Actor:
        
        if name in self.__actor_state:
            return self.__actor_state[name]

        profile = self.__ast_util.get_profile(name)
        act = Actor(pos)
        a={}
        sprites = profile.sprites.items()
        for dk, dv in sprites:
            for ak, av in dv.items():
                act.add_spritesheet(ak, dk, list(av.values()))

        act.speed = profile.speed
        act.name = profile.name
        act.immortal = profile.immortal
        act.set_sprite_mode(ANIM_STATE.FRONT_IDLE)

        return act

    def __init__(self) -> None:
        self.__actor_state = {}
        self.__ast_util = get_assetutil()