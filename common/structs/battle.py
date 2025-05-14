from typing import Dict, List, Optional
from enum import IntEnum, StrEnum
from pydantic import BaseModel
from proto import BattleBuff

from common.structs.monster import Monster
from common.structs.relic import SubAffix


class BattleType(StrEnum):
    DEFAULT = "DEFAULT"
    MOC = "MOC"
    PF = "PF"
    SU = "SU"
    AS = "AS"

    @staticmethod
    def default() -> "BattleType":
        return BattleType.DEFAULT

    def to_int(self) -> int:
        return {
            BattleType.DEFAULT: 0,
            BattleType.MOC: 1,
            BattleType.PF: 2,
            BattleType.SU: 3,
            BattleType.AS: 4,
        }.get(self, 0)


class DynamicKey(BaseModel):
    key: str = ""
    value: int = 0


class BattleBuffJson(BaseModel):
    level: int = 0
    id: int = 0
    dynamic_key: Optional[DynamicKey] = None
    dynamic_values: List[DynamicKey] = []

    def to_battle_buff_proto() -> BattleBuff:
        dynamic_values: Dict[str, float] = (
            {self.dynamic_key.key: float(self.dynamic_key.value)}
            if self.dynamic_key
            else {}
        )

        return BattleBuff(
            id=self.id,
            level=self.level,
            wave_flag=0xFFFFFFFF,
            owner_index=0xFFFFFFFF,
            dynamic_values=dynamic_values,
        )


class RogueMagicComponentType(IntEnum):
    Passive = 3
    Active = 4
    Attach = 5

    @staticmethod
    def default() -> "RogueMagicComponentType":
        return RogueMagicComponentType.Active


class RogueMagicComponent(BaseModel):
    id: int = 0
    level: int = 0
    component_type: RogueMagicComponentType = RogueMagicComponentType.default()


class RogueMagicScepter(BaseModel):
    level: int = 0
    id: int = 0
    components: List[RogueMagicComponent] = []


class BattleConfig(BaseModel):
    battle_type: BattleType = BattleType.default()
    monsters: List[List[Monster]] = [[Monster(level=60, monster_id=3014022, max_hp=0)]]
    blessings: List[BattleBuffJson] = []
    stage_id: int = 201012311
    cycle_count: int = 0
    path_resonance_id: int = 0
    custom_stats: List[SubAffix] = []
    scepters: List[RogueMagicScepter] = []
