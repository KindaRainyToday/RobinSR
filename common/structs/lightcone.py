from proto import BattleEquipment, Equipment, ItemType
from pydantic import BaseModel
from common.structs.util import get_item_unique_id


class Lightcone(BaseModel):
    level: int
    item_id: int
    equip_avatar: int
    rank: int
    promotion: int
    internal_uid: int

    def get_unique_id(self) -> int:
        return get_item_unique_id(self.internal_uid, ItemType.ITEM_EQUIPMENT)

    def to_equipment_proto(self) -> Equipment:
        return Equipment(
            equip_avatar_id=self.equip_avatar,
            exp=0,
            is_protected=False,
            level=self.level,
            promotion=self.promotion,
            rank=self.rank,
            tid=self.item_id,
            unique_id=self.get_unique_id(),
        )

    def to_battle_equipment_proto(self) -> BattleEquipment:
        return BattleEquipment(
            id=self.item_id,
            level=self.level,
            promotion=self.promotion,
            rank=self.rank,
        )
