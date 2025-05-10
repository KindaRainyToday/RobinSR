from proto import SceneMonster, SceneMonsterWave, SceneMonsterWaveParam
from pydantic import BaseModel
from typing import List


class Monster(BaseModel):
    level: int
    monster_id: int
    max_hp: int

    def to_scene_monster_proto(self) -> SceneMonster:
        return SceneMonster(
            monster_id=self.monster_id,
            max_hp=self.max_hp,
            cur_hp=self.max_hp,
        )

    @staticmethod
    def to_scene_monster_wave_proto(
        wave_id: int, monsters: List["Monster"]
    ) -> SceneMonsterWave:
        if wave_id < 1:
            wave_id += 1

        max_level = max((m.level for m in monsters), default=95)

        return SceneMonsterWave(
            wave_id=wave_id,
            wave_param=SceneMonsterWaveParam(
                level=max_level,
            ),
            monster_list=[m.to_scene_monster_proto() for m in monsters],
        )

    @staticmethod
    def to_scene_monster_waves(
        monsters: List[List["Monster"]],
    ) -> List[SceneMonsterWave]:
        return [
            Monster.to_scene_monster_wave_proto(i, wave)
            for i, wave in enumerate(monsters)
        ]
