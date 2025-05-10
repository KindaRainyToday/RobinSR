from typing import OrderedDict
from pydantic import BaseModel

from common.structs.avatar import MultiPathAvatar
from common.structs.scene import Position, Scene


class Persistent(BaseModel):
    lineups: OrderedDict[int, int] = OrderedDict(
        [
            (0, 1313),
            (1, 1006),
            (2, 8001),
            (3, 1405),
        ]
    )
    position: Position = Position()
    scene: Scene = Scene()
    main_character: MultiPathAvatar = MultiPathAvatar.FemaleRemembrance
    march_type: MultiPathAvatar = MultiPathAvatar.MarchHunt
