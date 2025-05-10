from pydantic import BaseModel
from enum import IntEnum
from typing import List, Dict
from pathlib import Path


class Vector(BaseModel):
    x: int
    y: int
    z: int


class PropState(IntEnum):
    Closed = 0
    Open = 1
    Locked = 2
    BridgeState1 = 3
    BridgeState2 = 4
    BridgeState3 = 5
    BridgeState4 = 6
    CheckPointDisable = 7
    CheckPointEnable = 8
    TriggerDisable = 9
    TriggerEnable = 10
    ChestLocked = 11
    ChestClosed = 12
    ChestUsed = 13
    Elevator1 = 14
    Elevator2 = 15
    Elevator3 = 16
    WaitActive = 17
    EventClose = 18
    EventOpen = 19
    Hidden = 20
    TeleportGate0 = 21
    TeleportGate1 = 22
    TeleportGate2 = 23
    TeleportGate3 = 24
    Destructed = 25
    CustomState01 = 101
    CustomState02 = 102
    CustomState03 = 103
    CustomState04 = 104
    CustomState05 = 105
    CustomState06 = 106
    CustomState07 = 107
    CustomState08 = 108
    CustomState09 = 109


class PlaneType(IntEnum):
    Unknown = 0
    Maze = 2
    Train = 3
    Challenge = 4
    Rogue = 5
    Raid = 6
    AetherDivide = 7
    TrialActivity = 8
    Town = 1


class SceneMonsterInfo(BaseModel):
    pos: Vector
    rot: Vector
    groupId: int
    instId: int
    monsterId: int
    eventId: int


class SceneNpcInfo(BaseModel):
    pos: Vector
    rot: Vector
    groupId: int
    instId: int
    npcId: int


class ScenePropInfo(BaseModel):
    pos: Vector
    rot: Vector
    groupId: int
    instId: int
    propState: int
    propId: int


class TeleportInfo(BaseModel):
    pos: Vector
    rot: Vector


class SceneData(BaseModel):
    npcs: List[SceneNpcInfo]
    props: List[ScenePropInfo]
    monsters: List[SceneMonsterInfo]
    teleports: Dict[int, TeleportInfo]


class LevelOutputConfig(BaseModel):
    isEnteredSceneInfo: bool
    scenes: Dict[int, SceneData]
    planeType: int
    worldId: int


class AvatarConfig(BaseModel):
    weaknessBuffId: int


class JsonConfig(BaseModel):
    levelOutputConfigs: Dict[int, Dict[str, LevelOutputConfig]]
    avatarConfigs: Dict[int, AvatarConfig]
    mapDefaultEntranceMap: Dict[int, int]


GAME_RES: JsonConfig = JsonConfig.model_validate_json(Path("res.json").read_text())
