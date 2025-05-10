import proto
from proto import BattleRelic, EquipRelic, ItemType, RelicAffix
from pydantic import BaseModel
from typing import List
from common.structs.util import get_item_unique_id


class SubAffix(BaseModel):
    sub_affix_id: int
    count: int
    step: int

    def to_relic_affix_proto(self) -> RelicAffix:
        return RelicAffix(
            affix_id=self.sub_affix_id,
            cnt=self.count,
            step=self.step,
        )


class Relic(BaseModel):
    level: int
    relic_id: int
    main_affix_id: int
    sub_affixes: List[SubAffix]
    internal_uid: int
    equip_avatar: int

    def get_slot(self) -> int:
        return self.relic_id % 10

    def is_matching_slot(self, slot: int) -> bool:
        return self.get_slot() == slot

    def get_unique_id(self) -> int:
        return get_item_unique_id(self.internal_uid, ItemType.ITEM_RELIC)

    def to_battle_relic_proto(self) -> BattleRelic:
        return BattleRelic(
            id=self.relic_id,
            level=self.level,
            main_affix_id=self.main_affix_id,
            unique_id=self.get_unique_id(),
            sub_affix_list=[s.to_relic_affix_proto() for s in self.sub_affixes],
        )

    def to_equip_relic_proto(self) -> EquipRelic:
        return EquipRelic(
            type=self.get_slot(),
            relic_unique_id=self.get_unique_id(),
        )

    def to_relic_proto(self) -> proto.Relic:
        return proto.Relic(
            equip_avatar_id=self.equip_avatar,
            exp=0,
            is_protected=False,
            level=self.level,
            main_affix_id=self.main_affix_id,
            tid=self.relic_id,
            unique_id=self.get_unique_id(),
            sub_affix_list=[s.to_relic_affix_proto() for s in self.sub_affixes],
        )
