from typing import OrderedDict, Dict, List, Optional
from enum import StrEnum
from pydantic import BaseModel

from proto import (
    Avatar,
    AvatarSkillTree,
    AvatarType,
    BattleAvatar,
    BattleBuff,
    ExtraLineupType,
    Gender,
    LineupAvatar,
    LineupInfo,
    MultiPathAvatarType,
    SpBarInfo,
    MultiPathAvatarInfo,
)

from common.structs.lightcone import Lightcone
from common.structs.relic import Relic


class MultiPathAvatar(StrEnum):
    MalePhysical = "MalePhysical"
    FemalePhysical = "FemalePhysical"
    MalePreservation = "MalePreservation"
    FemalePreservation = "FemalePreservation"
    MaleHarmony = "MaleHarmony"
    FemaleHarmony = "FemaleHarmony"
    MaleRemembrance = "MaleRemembrance"
    FemaleRemembrance = "FemaleRemembrance"
    MarchHunt = "MarchHunt"
    MarchPreservation = "MarchPreservation"
    Unk = "Unk"

    def to_int(self) -> int:
        return {
            MultiPathAvatar.MalePhysical: 8001,
            MultiPathAvatar.FemalePhysical: 8002,
            MultiPathAvatar.MalePreservation: 8003,
            MultiPathAvatar.FemalePreservation: 8004,
            MultiPathAvatar.MaleHarmony: 8005,
            MultiPathAvatar.FemaleHarmony: 8006,
            MultiPathAvatar.MarchHunt: 1224,
            MultiPathAvatar.MarchPreservation: 1001,
            MultiPathAvatar.MaleRemembrance: 8007,
            MultiPathAvatar.FemaleRemembrance: 8008,
        }.get(self, 0)

    @staticmethod
    def from_int(value: int) -> "MultiPathAvatar":
        return {
            8001: MultiPathAvatar.MalePhysical,
            8002: MultiPathAvatar.FemalePhysical,
            8003: MultiPathAvatar.MalePreservation,
            8004: MultiPathAvatar.FemalePreservation,
            8005: MultiPathAvatar.MaleHarmony,
            8006: MultiPathAvatar.FemaleHarmony,
            1224: MultiPathAvatar.MarchHunt,
            1001: MultiPathAvatar.MarchPreservation,
            8007: MultiPathAvatar.MaleRemembrance,
            8008: MultiPathAvatar.FemaleRemembrance,
        }.get(value, MultiPathAvatar.Unk)

    def get_gender(self) -> Gender:
        id = self.to_int()
        if id < 8000:
            return Gender.GenderNone
        elif id & 1 == 1:
            return Gender.GenderMan
        else:
            return Gender.GenderWoman

    def get_type(self) -> MultiPathAvatarType:
        return {
            MultiPathAvatar.MalePhysical: MultiPathAvatarType.BoyWarriorType,
            MultiPathAvatar.FemalePhysical: MultiPathAvatarType.GirlWarriorType,
            MultiPathAvatar.MalePreservation: MultiPathAvatarType.BoyKnightType,
            MultiPathAvatar.FemalePreservation: MultiPathAvatarType.GirlKnightType,
            MultiPathAvatar.MaleHarmony: MultiPathAvatarType.BoyShamanType,
            MultiPathAvatar.FemaleHarmony: MultiPathAvatarType.GirlShamanType,
            MultiPathAvatar.MarchHunt: MultiPathAvatarType.Mar_7thRogueType,
            MultiPathAvatar.MarchPreservation: MultiPathAvatarType.Mar_7thKnightType,
            MultiPathAvatar.MaleRemembrance: MultiPathAvatarType.BoyMemoryType,
            MultiPathAvatar.FemaleRemembrance: MultiPathAvatarType.GirlMemoryType,
            MultiPathAvatar.Unk: MultiPathAvatarType.MultiPathAvatarTypeNone,
        }.get(self, MultiPathAvatarType.MultiPathAvatarTypeNone)

    def is_mc(self) -> bool:
        return self.to_int() > 8000

    @staticmethod
    def to_list() -> List["MultiPathAvatar"]:
        return list(MultiPathAvatar)


class AvatarData(BaseModel):
    rank: int
    skills: Dict[int, int]


class AvatarJson(BaseModel):
    avatar_id: int
    data: AvatarData
    level: int
    promotion: int
    techniques: List[int]
    sp_value: Optional[int]
    sp_max: Optional[int]

    def to_avatar_proto(
        self, lightcone: Optional[Lightcone], relics: List[Relic]
    ) -> Avatar:
        if self.avatar_id > 8000:
            base_avatar_id = 8001
        elif self.avatar_id in [1001, 1224]:
            base_avatar_id = 1001
        else:
            base_avatar_id = self.avatar_id

        skilltree_list = [
            AvatarSkillTree(point_id=k, level=v) for k, v in self.data.skills.items()
        ]

        equip_relic_list = [r.to_equip_relic_proto() for r in relics]

        return Avatar(
            base_avatar_id=base_avatar_id,
            level=self.level,
            promotion=self.promotion,
            rank=self.data.rank,
            skilltree_list=skilltree_list,
            equipment_unique_id=lightcone.get_unique_id() if lightcone else 0,
            first_met_time_stamp=1712924677,
            equip_relic_list=equip_relic_list,
        )

    def to_avatar_multipath_proto(
        self, lightcone: Optional[Lightcone], relics: List[Relic]
    ) -> MultiPathAvatarInfo:
        skilltree_list = [
            AvatarSkillTree(point_id=k, level=v) for k, v in self.data.skills.items()
        ]

        equip_relic_list = [r.to_equip_relic_proto() for r in relics]

        return MultiPathAvatarInfo(
            avatar_id=self.avatar_id,
            rank=self.data.rank,
            equip_relic_list=equip_relic_list,
            multi_path_skill_tree=skilltree_list,
            path_equipment_id=lightcone.get_unique_id() if lightcone else 0,
            dressed_skin_id=0,
        )

    def to_battle_avatar_proto(
        self, index: int, lightcone: Optional[Lightcone], relics: List[Relic]
    ) -> tuple[BattleAvatar, List[BattleBuff]]:
        skilltree_list = [
            AvatarSkillTree(point_id=k, level=v) for k, v in self.data.skills.items()
        ]

        relic_list = [r.to_battle_relic_proto() for r in relics]

        if lightcone:
            equipment_list = [lightcone.to_battle_equipment_proto()]
        else:
            equipment_list = []

        battle_avatar = BattleAvatar(
            index=index,
            avatar_type=AvatarType.AVATAR_UPGRADE_AVAILABLE_TYPE,
            id=self.avatar_id,
            level=self.level,
            rank=self.data.rank,
            skilltree_list=skilltree_list,
            equipment_list=equipment_list,
            hp=10000,
            promotion=self.promotion,
            relic_list=relic_list,
            world_level=6,
            sp_bar=SpBarInfo(
                cur_sp=self.sp_value if self.sp_value else 10000,
                max_sp=self.sp_max if self.sp_max else 10000,
            ),
        )

        battle_buff = [
            BattleBuff(
                wave_flag=0xFFFFFFFF,
                owner_id=index,
                level=1,
                id=buff_id,
                dynamic_values={"SkillIndex": 2.0},
            )
            for buff_id in self.techniques
        ]

        return (battle_avatar, battle_buff)

    def to_lineup_avatar_proto(self, slot: int) -> LineupAvatar:
        return LineupAvatar(
            id=self.avatar_id,
            hp=10000,
            satiety=100,
            avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
            sp_bar=SpBarInfo(
                cur_sp=self.sp_value if self.sp_value else 10000,
                max_sp=self.sp_max if self.sp_max else 10000,
            ),
            slot=slot,
        )

    @staticmethod
    def to_lineup_avatars(player: "FreesrData") -> List[LineupAvatar]:
        avatar_ids = {avatar.avatar_id for avatar in player.avatars.values()}

        return [
            player.avatars[avatar_id].to_lineup_avatar_proto(slot)
            for slot, avatar_id in player.lineups.items()
            if slot < 4 and avatar_id > 0 and avatar_id in avatar_ids
        ]

    @staticmethod
    def to_lineup_info(lineups: OrderedDict[int, int]) -> LineupInfo:
        lineup_info = LineupInfo(
            extra_lineup_type=ExtraLineupType.LINEUP_NONE,
            name="Squad 1",
            mp=5,
            max_mp=5,
        )

        for avatar_id in lineups.values():
            if avatar_id == 0:
                continue
            lineup_info.avatar_list.append(
                LineupAvatar(
                    id=avatar_id,
                    hp=10000,
                    satiety=100,
                    avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
                    sp_bar=SpBarInfo(cur_sp=10000, max_sp=10000),
                    slot=len(lineup_info.avatar_list),
                )
            )

        return lineup_info
