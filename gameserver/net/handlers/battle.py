from common.resources import GAME_RES
from common.structs.battle import BattleType, RogueMagicComponentType
from common.structs.monster import Monster
from common.util import Logger
from random import randint
from proto import *


# why is this even async in the original code?
def create_battle_info(
    session: "PlayerSession",
    caster_id: int,
    skill_index: int,
) -> SceneBattleInfo:
    battle_info = SceneBattleInfo(
        stage_id=session.json_data.battle_config.stage_id,
        logic_random_seed=randint(0, 0xFFFFFFFF),
        battle_id=1,
        rounds_limit=session.json_data.battle_config.cycle_count,
        world_level=6,
    )

    for avatar_index, avatar_id in session.json_data._lineups.items():
        is_trailblazer = avatar_id == 8001
        is_march = avatar_id == 1001

        if is_trailblazer:
            avatar_id = session.json_data.main_character.to_int()
        elif is_march:
            avatar_id = session.json_data.march_type.to_int()

        if avatar := session.json_data.avatars.get(avatar_id):
            battle_avatar, techs = session.json_data.get_battle_avatar_proto(
                avatar_index, avatar_id
            )

            for tech in techs:
                battle_info.buff_list.append(tech)

            avatar_config = GAME_RES.avatarConfigs.get(avatar_id)

            if (
                caster_id > 0
                and avatar_index == (caster_id - 1)
                and avatar_config
                and 1000119 not in avatar.techniques
            ):
                battle_info.buff_list.append(
                    BattleBuff(
                        id=avatar_config.weaknessBuffId,
                        level=1,
                        owner_index=avatar_index,
                        wave_flag=0xFFFFFFFF,
                        dynamic_values={"SkillIndex": float(skill_index)},
                    )
                )

            battle_info.battle_avatar_list.append(battle_avatar)

            if avatar_id == 1224:
                buffs = BattleBuff(
                    id=122401,
                    level=3,
                    wave_flag=0xFFFFFFFF,
                    owner_index=avatar_index,
                    dynamic_values={
                        "#ADF_1": 3.0,
                        "#ADF_2": 3.0,
                    },
                    target_index_list=[0],
                )

                battle_info.buff_list.append(buffs)

    for stat in session.json_data.battle_config.custom_stats:
        for avatar in battle_info.battle_avatar_list:
            if len(avatar.relic_list) == 0:
                avatar.relic_list.append(
                    BattleRelic(
                        id=61011,
                        main_affix_id=1,
                        level=1,
                    )
                )

            sub_affix = next(
                (
                    v
                    for v in avatar.relic_list[0].sub_affix_list
                    if v.affix_id == stat.sub_affix_id
                ),
                None,
            )

            if sub_affix:
                sub_affix.cnt = stat.count
            else:
                avatar.relic_list[0].sub_affix_list.append(
                    RelicAffix(
                        affix_id=stat.sub_affix_id,
                        cnt=stat.count,
                        step=stat.step,
                    )
                )

    for blessing in session.json_data.battle_config.blessings:
        buffs = BattleBuff(
            id=blessing.id,
            level=blessing.level,
            wave_flag=0xFFFFFFFF,
            owner_index=0xFFFFFFFF,
        )

        if blessing.dynamic_key is not None:
            buffs.dynamic_values[blessing.dynamic_key.key] = (
                blessing.dynamic_key.dynamic_value
            )

        for dynamic_value in blessing.dynamic_values:
            if dynamic_value.key in buffs.dynamic_values:
                continue

            buffs.dynamic_values[dynamic_value.key] = dynamic_value.value

        battle_info.buff_list.append(buffs)

    if session.json_data.battle_config.battle_type == BattleType.PF:
        if battle_info.stage_id >= 30309011:
            battle_info.battle_target_info[1] = BattleTargetList(
                battle_target_list=[
                    BattleTarget(
                        id=10003,
                    )
                ]
            )
        else:
            battle_info.battle_target_info[1] = BattleTargetList(
                battle_target_list=[
                    BattleTarget(
                        id=10002,
                    )
                ]
            )

        for i in range(2, 5):
            battle_info.battle_target_info[i] = BattleTargetList()

        battle_info.battle_target_info[5] = BattleTargetList(
            battle_target_list=[
                BattleTarget(
                    id=2001,
                ),
                BattleTarget(
                    id=2002,
                ),
            ]
        )

    if session.json_data.battle_config.battle_type == BattleType.AS:
        battle_info.battle_target_info[1] = BattleTargetList(
            battle_target_list=[BattleTarget(id=90005)]
        )

    if session.json_data.battle_config.battle_type == BattleType.SU:
        # lazy
        # would be annoying to update later on anyways.
        raise Exception("SU battle is not implemented!!!")

    battle_info.monster_wave_list = Monster.to_scene_monster_waves(
        session.json_data.battle_config.monsters
    )

    # global buff
    if not any(b.id == 140703 for b in battle_info.buff_list):
        battle_info.buff_list.append(
            BattleBuffJson(
                id=140703,
                level=1,
                owner_index=0xFFFFFFFF,
                wave_flag=0xFFFFFFFF,
            )
        )

    return battle_info


async def on_start_cocoon_stage_cs_req(
    session: "PlayerSession",
    req: StartCocoonStageCsReq,
    rsp: StartCocoonStageScRsp,
) -> None:
    rsp.prop_entity_id = req.prop_entity_id
    rsp.cocoon_id = req.cocoon_id
    rsp.wave = req.wave
    rsp.battle_info = create_battle_info(session, 0, 0)


async def on_quick_start_cocoon_stage_cs_req(
    session: "PlayerSession",
    req: QuickStartCocoonStageCsReq,
    rsp: QuickStartCocoonStageScRsp,
) -> None:
    battle_info = create_battle_info(session, 0, 0)
    battle_info.world_level = req.world_level

    rsp.cocoon_id = req.cocoon_id
    rsp.wave = req.wave
    rsp.battle_info = battle_info


async def on_pve_battle_result_cs_req(
    _session: "PlayerSession",
    req: PVEBattleResultCsReq,
    res: PVEBattleResultScRsp,
) -> None:
    res.end_status = req.end_status
    res.battle_id = req.battle_id


async def on_scene_cast_skill_cs_req(
    session: "PlayerSession",
    req: SceneCastSkillCsReq,
    res: SceneCastSkillScRsp,
) -> None:
    targets = [
        eid
        for eid in req.hit_target_entity_id_list + req.assist_monster_entity_id_list
        if eid > 30_000 or eid < 1_000
    ]

    if len(targets) == 0:
        Logger.warn("SceneCastSkill target is empty")

    res.cast_entity_id = req.cast_entity_id
    res.battle_info = create_battle_info(
        session, req.attacked_by_entity_id, req.skill_index
    )
