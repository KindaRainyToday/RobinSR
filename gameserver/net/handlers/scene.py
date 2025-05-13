from common.resources import GAME_RES
from common.structs.avatar import AvatarJson
from common.structs.scene import Position
from common.util import Logger
from gameserver.util import cur_timestamp_secs
from typing import List, Optional
from proto import *


async def load_scene(
    session: "PlayerSession",
    entry_id: int,
    is_enter_scene: bool,
    teleport_id: Optional[int],
) -> Optional[SceneInfo]:
    entry = GAME_RES.levelOutputConfigs.get(entry_id)
    first_item = next(iter(entry.items()), None) if entry else None

    if first_item is not None:
        name, scene = first_item
    else:
        Logger.error(f"Map entrance not found: {entry_id}")
        return None

    try:
        split = name.split("_")
        plane_id = int(split[0][1:])
        floor_id = int(split[1][1:])
    except:
        Logger.error(f"Invalid map name format: {name}")
        return None

    if teleport_id:
        teleport = None

        for _, s in scene.scenes.items():
            if teleport_id in s.teleports:
                teleport = s.teleports[teleport_id]
                break

        if teleport is None:
            for _, s in scene.scenes.items():
                if s.teleports:
                    teleport = next(iter(s.teleports.values()))
                    break

        if teleport:
            session.json_data._position.x = teleport.pos.x
            session.json_data._position.y = teleport.pos.y
            session.json_data._position.z = teleport.pos.z
            session.json_data._position.rot_y = teleport.rot.y

    scene_info = SceneInfo(
        floor_id=floor_id,
        plane_id=plane_id,
        entry_id=entry_id,
        game_mode_type=scene.planeType,
        leader_entity_id=1,
        world_id=501 if scene.worldId == 100 else scene.worldId,
    )

    loaded_npc: List[int] = []
    prop_entity_id = 1000
    npc_entity_id = 20000
    monster_entity_id = 30000

    for group_id, group in scene.scenes.items():
        group_info = SceneEntityGroupInfo(group_id=group_id)

        if not group.props and not group.npcs and not group.monsters:
            continue

        for prop in group.props:
            prop_entity_id += 1

            prop_position = Position(
                x=prop.pos.x,
                y=prop.pos.y,
                z=prop.pos.z,
                rot_y=prop.rot.y,
            )

            entity_info = SceneEntityInfo(
                inst_id=prop.instId,
                group_id=prop.groupId,
                motion=prop_position.to_motion_info_proto(),
                prop=ScenePropInfo(
                    prop_state=prop.propState,
                    prop_id=prop.propId,
                ),
                entity_id=prop_entity_id,
            )

            group_info.entity_list.append(entity_info)

        for npc in group.npcs:
            if npc.npcId in loaded_npc or npc.npcId in session.json_data.avatars:
                continue

            npc_entity_id += 1
            loaded_npc.append(npc.npcId)

            npc_position = Position(
                x=npc.pos.x,
                y=npc.pos.y,
                z=npc.pos.z,
                rot_y=npc.rot.y,
            )

            entity_info = SceneEntityInfo(
                inst_id=npc.instId,
                group_id=npc.groupId,
                entity_id=npc_entity_id,
                motion=npc_position.to_motion_info_proto(),
                npc=SceneNpcInfo(
                    npc_id=npc.npcId,
                ),
            )
            group_info.entity_list.append(entity_info)

        for monster in group.monsters:
            monster_entity_id += 1
            monster_position = Position(
                x=monster.pos.x,
                y=monster.pos.y,
                z=monster.pos.z,
                rot_y=monster.rot.y,
            )
            npc_monster = SceneNpcMonsterInfo(
                monster_id=monster.monsterId,
                event_id=monster.eventId,
                world_level=6,
            )
            entity_info = SceneEntityInfo(
                inst_id=monster.instId,
                group_id=monster.groupId,
                entity_id=monster_entity_id,
                motion=monster_position.to_motion_info_proto(),
                npc_monster=npc_monster,
            )
            group_info.entity_list.append(entity_info)

        scene_info.entity_group_list.append(group_info)

        scene_info.group_state_list.append(
            SceneGroupState(
                group_id=group_id,
                is_default=True,
                state=0,
            )
        )

    scene_info.entity_group_list.append(
        SceneEntityGroupInfo(
            entity_list=[
                SceneEntityInfo(
                    entity_id=slot + 1,
                    motion=session.json_data._position.to_motion_info_proto(),
                    actor=SceneActorInfo(
                        avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
                        base_avatar_id=avatar_id,
                        uid=25,
                    ),
                )
                for slot, avatar_id in session.json_data._lineups.items()
            ]
        )
    )

    if is_enter_scene:
        lineup_info = AvatarJson.to_lineup_info(session.json_data._lineups)
        session.json_data._scene.entry_id = entry_id
        session.json_data._scene.floor_id = floor_id
        session.json_data._scene.plane_id = plane_id
        session.json_data._position.x = session.json_data._position.x
        session.json_data._position.y = session.json_data._position.y
        session.json_data._position.z = session.json_data._position.z
        session.json_data._position.rot_y = session.json_data._position.rot_y
        await session.json_data.save_persistent()

        session.send(
            cmd_id=CmdID.EnterSceneByServerScNotify,
            body=EnterSceneByServerScNotify(
                scene=scene_info,
                lineup=lineup_info,
            ),
        )

    return scene_info


async def on_get_cur_scene_info_cs_req(
    session: "PlayerSession",
    _body: GetCurSceneInfoCsReq,
    res: GetCurSceneInfoScRsp,
) -> None:
    if scene := await load_scene(
        session, session.json_data._scene.entry_id, False, None
    ):
        res.scene = scene
    else:
        res.scene = SceneInfo(
            game_mode_type=3,
            entry_id=session.json_data._scene.entry_id,
            plane_id=session.json_data._scene.plane_id,
            floor_id=session.json_data._scene.floor_id,
        )


async def on_enter_scene_cs_req(
    session: "PlayerSession",
    req: EnterSceneCsReq,
    res: EnterSceneScRsp,
) -> None:
    scene = await load_scene(session, req.entry_id, true, Some(req.teleport_id))
    if not scene:
        res.retcode = int(Retcode.RET_SCENE_ENTRY_ID_NOT_MATCH)


async def on_get_scene_map_info_cs_req(
    _session: "PlayerSession",
    req: GetSceneMapInfoCsReq,
    res: GetSceneMapInfoScRsp,
) -> None:
    for floor_id in req.floor_id_list:
        map_info = SceneMapInfo(
            chest_list=[
                ChestInfo(chest_type=ChestType.MAP_INFO_CHEST_TYPE_NORMAL),
                ChestInfo(chest_type=ChestType.MAP_INFO_CHEST_TYPE_CHALLENGE),
                ChestInfo(chest_type=ChestType.MAP_INFO_CHEST_TYPE_PUZZLE),
            ]
        )

        for i in range(0, 100):
            map_info.lighten_section_list.append(i)

        group_config = None
        entrance_id = GAME_RES.mapDefaultEntranceMap.get(floor_id)

        if entrance_id:
            entry = GAME_RES.levelOutputConfigs.get(entrance_id)
            if entry:
                group_config = next(iter(entry.items()), None)

        if group_config:
            _, config = group_config

            for group_id, group in config.scenes.items():
                map_info.maze_group_list.append(MazeGroup(group_id=group_id))

                for teleport_id in group.teleports.keys():
                    map_info.unlock_teleport_list.append(teleport_id)

                for prop in group.props:
                    map_info.maze_prop_list.append(
                        MazePropState(
                            group_id=prop.groupId,
                            state=prop.propState,
                            config_id=prop.instId,
                        )
                    )

        res.scene_map_info.append(map_info)


async def on_scene_entity_move_cs_req(
    session: "PlayerSession",
    req: SceneEntityMoveCsReq,
    _res: SceneEntityMoveScRsp,
) -> None:
    if session.next_scene_save >= cur_timestamp_secs():
        return

    session.next_scene_save = cur_timestamp_secs() + 5

    for entity in req.entity_motion_list:
        if entity.entity_id != 0:
            continue

        session.json_data._position.x = entity.motion.pos.x
        session.json_data._position.y = entity.motion.pos.y
        session.json_data._position.z = entity.motion.pos.z
        session.json_data._position.rot_y = entity.motion.rot.y

    await session.json_data.save_persistent()


async def on_get_entered_scene_cs_req(
    _session: "PlayerSession",
    _req: GetEnteredSceneCsReq,
    res: GetEnteredSceneScRsp,
) -> None:
    res.entered_scene_info = []

    for entry_dict in GAME_RES.levelOutputConfigs.values():
        for name, config in entry_dict.items():
            if config.isEnteredSceneInfo:
                try:
                    split = name.split("_")
                    plane_id = int(split[0][1:])
                    floor_id = int(split[1][1:])
                    res.entered_scene_info.append(
                        EnteredSceneInfo(plane_id=plane_id, floor_id=floor_id)
                    )
                except Exception:
                    Logger.error(f"Invalid scene key format: {name}")
