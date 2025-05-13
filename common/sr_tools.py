from proto import Avatar, AvatarSkillTree, MultiPathAvatarInfo
from pydantic import BaseModel, PrivateAttr
from typing import OrderedDict, Dict, List, Optional
from pathlib import Path
import asyncio

from common.util import AsyncFs, SyncFs
from common.structs.avatar import AvatarJson, MultiPathAvatar
from common.structs.lightcone import Lightcone
from common.structs.relic import Relic
from common.structs.battle import BattleConfig
from common.structs.persistent import Persistent
from common.structs.scene import Position, Scene

PERSISTENT_FILE = "persistent.json"
FREESR_FILE = "freesr-data.json"


class FreesrData(BaseModel):
    avatars: Dict[int, AvatarJson]
    lightcones: List[Lightcone]
    relics: List[Relic]
    battle_config: Optional[BattleConfig] = None
    _lineups: OrderedDict[int, int] = PrivateAttr()
    _position: Position = PrivateAttr()
    _scene: Scene = PrivateAttr()
    _main_character: MultiPathAvatar = PrivateAttr()
    _march_type: MultiPathAvatar = PrivateAttr()
    _freesr_last_write: int = PrivateAttr()

    def get_avatar_proto(self, avatar_id: int) -> Optional[Avatar]:
        if avatar := self.avatars.get(avatar_id):
            lightcone = next(
                (l for l in self.lightcones if l.equip_avatar == avatar_id), None
            )
            relics = [r for r in self.relics if r.equip_avatar == avatar_id]

            return avatar.to_avatar_proto(lightcone, relics)
        return None

    def get_avatar_multipath_proto(
        self, avatar_id: int
    ) -> Optional[MultiPathAvatarInfo]:
        if avatar := self.avatars.get(avatar_id):
            if mp_type := MultiPathAvatar.from_int(avatar_id):
                if mp_type is MultiPathAvatar.Unk:
                    return None

                lightcone = next(
                    (l for l in self.lightcones if l.equip_avatar == avatar_id), None
                )
                relics = [r for r in self.relics if r.equip_avatar == avatar_id]

                return avatar.to_avatar_multipath_proto(lightcone, relics)
            return None
        return None

    def get_multi_path_info(self) -> List[MultiPathAvatarInfo]:
        result = []
        for mp_type in MultiPathAvatar.to_list():
            if (
                mp_type.is_mc()
                and mp_type.get_gender() != self._main_character.get_gender()
            ):
                continue
            avatar_id = mp_type.to_int()
            if avatar := self.avatars.get(avatar_id):
                lightcone = next(
                    (l for l in self.lightcones if l.equip_avatar == avatar_id), None
                )
                relics = [r for r in self.relics if r.equip_avatar == avatar_id]

                result.append(avatar.to_avatar_multipath_proto(lightcone, relics))
            continue
        return result

    async def save_persistent(self) -> None:
        persistent = Persistent(
            lineups=self._lineups,
            main_character=self._main_character,
            position=self._position,
            scene=self._scene,
            march_type=self._march_type,
        )
        await AsyncFs.write_to_file(
            PERSISTENT_FILE, persistent.model_dump_json(indent=2)
        )

    async def verify_lineup(self) -> None:
        lineup_len = len(self._lineups)
        if lineup_len == 0:
            self._lineups = OrderedDict([(0, 8001), (1, 0), (2, 0), (3, 0)])
        elif lineup_len < 4:
            for i in range(lineup_len, 4):
                self._lineups[i] = 0
        await self.save_persistent()

    @staticmethod
    def get_last_write_time() -> None:
        return SyncFs.get_last_modified_time(FREESR_FILE)

    @staticmethod
    async def load() -> "FreesrData":
        freesr_data_json, persistent_json = await asyncio.gather(
            AsyncFs.read_to_str(FREESR_FILE),
            AsyncFs.read_to_str(PERSISTENT_FILE),
        )

        freesr_data = FreesrData.model_validate_json(freesr_data_json)
        persistent_data = Persistent.model_validate_json(persistent_json)

        freesr_data._lineups = persistent_data.lineups
        freesr_data._position = persistent_data.position
        freesr_data._scene = persistent_data.scene
        freesr_data._main_character = persistent_data.main_character
        freesr_data._march_type = persistent_data.march_type
        freesr_data._freesr_last_write = FreesrData.get_last_write_time()

        # clean up unequipped stuff
        lc_count = len(freesr_data.lightcones)
        relic_count = len(freesr_data.relics)

        if lc_count > 1500:
            freesr_data.lightcones = [
                lc for lc in freesr_data.lightcones if lc.equip_avatar != 0
            ]
        if relic_count > 2000:
            freesr_data.relics = [r for r in freesr_data.relics if r.equip_avatar != 0]

        march_t = freesr_data._march_type.to_int()
        if march_t > 8000 or march_t == 0:
            freesr_data._march_type = MultiPathAvatar.MarchHunt

        await freesr_data.verify_lineup()

        return freesr_data

    async def update(self) -> None:
        if self.get_last_write_time() > self._freesr_last_write:
            new = await self.load()
            self.avatars = new.avatars
            self.lightcones = new.lightcones
            self.relics = new.relics
            self.battle_config = new.battle_config
            self._lineups = new._lineups
            self._position = new._position
            self._scene = new._scene
            self._main_character = new._main_character
            self._march_type = new._march_type
