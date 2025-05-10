from proto import ItemType


def get_item_unique_id(internal_uid: int, item_type: ItemType) -> int:
    if item_type == ItemType.ITEM_EQUIPMENT:
        return 2000 + internal_uid
    else:
        return 1 + internal_uid
