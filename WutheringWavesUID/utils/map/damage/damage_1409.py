# 卡提希娅
# 普攻4段命中附加1层【风蚀伤害】
# 小卡共鸣技能附加2层【风蚀伤害】
# 变奏技能2层【风蚀伤害】
# 2链释放1段大 3层【风蚀伤害】
from typing import Literal

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    attack_damage,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_skill,
    liberation_damage,
    skill_damage_calc,
)
from ...map.damage.buff import fengzhu_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    skill_name: Literal[
        "小卡普攻1段",
        "小卡普攻2段",
        "小卡普攻3段",
        "小卡普攻4段",
        "小卡重击",
        "小卡空中攻击",
        "小卡空中回收1剑",
        "小卡空中回收2剑",
        "小卡空中回收3剑",
    ] = "小卡普攻1段",
) -> tuple[str, str]:
    attr.set_env_aero_erosion()
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_life")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "常态攻击"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    if skill_name == "小卡普攻1段":
        skillParamId = "1"
    elif skill_name == "小卡普攻2段":
        skillParamId = "2"
    elif skill_name == "小卡普攻3段":
        skillParamId = "3"
    elif skill_name == "小卡普攻4段":
        skillParamId = "4"
    elif skill_name == "小卡重击":
        skillParamId = "8"
    elif skill_name == "小卡空中攻击":
        skillParamId = "9"
    elif skill_name == "小卡空中回收1剑":
        skillParamId = "10"
    elif skill_name == "小卡空中回收2剑":
        skillParamId = "11"
    elif skill_name == "小卡空中回收3剑":
        skillParamId = "12"
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], skillParamId, skillLevel
    )

    title = skill_name
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 风蚀效应层数 默认3层
    aeroErosionNum = 3
    if isGroup and (1406 in attr.teammate_char_ids or 1408 in attr.teammate_char_ids):
        aeroErosionNum += 3

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        pass

    if chain_num >= 2 and ("普攻" in skill_name or "重击" in skill_name):
        title = f"{role_name}-二链"
        msg = "小卡普攻技能倍率提升50%"
        attr.add_skill_ratio(0.5, title, msg)

    elif chain_num >= 2 and ("空中" in skill_name):
        title = f"{role_name}-二链"
        msg = "小卡空中攻击倍率提升200%"
        attr.add_skill_ratio(2, title, msg)

    if chain_num >= 2:
        aeroErosionNum += 3

    if chain_num >= 3:
        pass

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "附加【异常反应】，全属性伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 5:
        pass

    if chain_num >= 6:
        pass

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 默认吃满吧
        title = f"{role_name}-以风刻痕留蚀"
        msg = "小卡对其造成的伤害提升30%；"
        attr.add_dmg_bonus(0.3, title, msg)

        aeroErosionNumTemp = min(aeroErosionNum - 3, 3)
        if aeroErosionNumTemp > 0:
            title = f"{role_name}-以风刻痕留蚀"
            msg = f"3层风蚀，对其造成的伤害额外提升10%*{aeroErosionNumTemp}"
            attr.add_dmg_bonus(0.1 * aeroErosionNumTemp, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_life = attr.effect_life
    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_life):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_life):,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    attr.set_env_aero_erosion()
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_life")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣技能"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "6", skillLevel
    )

    title = "小卡共鸣技能"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 风蚀效应层数 默认3层
    aeroErosionNum = 3
    if isGroup and (1406 in attr.teammate_char_ids or 1408 in attr.teammate_char_ids):
        aeroErosionNum += 3

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        pass

    if chain_num >= 2:
        aeroErosionNum += 3

    if chain_num >= 3:
        pass

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "角色为目标附加【异常反应】后，使队伍中所有角色全属性伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 5:
        pass

    if chain_num >= 6:
        pass

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 默认吃满吧
        title = f"{role_name}-以风刻痕留蚀"
        msg = "小卡对其造成的伤害提升30%；"
        attr.add_dmg_bonus(0.3, title, msg)

        aeroErosionNumTemp = min(aeroErosionNum - 3, 3)
        if aeroErosionNumTemp > 0:
            title = f"{role_name}-以风刻痕留蚀"
            msg = f"3层风蚀，对其造成的伤害额外提升10%*{aeroErosionNumTemp}"
            attr.add_dmg_bonus(0.1 * aeroErosionNumTemp, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_life = attr.effect_life
    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_life):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_life):,.0f}"
    return crit_damage, expected_damage


def calc_damage_11(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    skill_name: Literal[
        "大卡普攻1段",
        "大卡普攻2段",
        "大卡普攻3段",
        "大卡普攻4段",
        "大卡普攻5段",
        "大卡重击",
        "大卡强化重击",
        "大卡空中1段",
        "大卡空中2段",
        "大卡空中3段",
    ] = "大卡普攻1段",
) -> tuple[str, str]:
    attr.set_env_aero_erosion()
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_life")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    if skill_name == "大卡普攻1段":
        skillParamId = "13"
    elif skill_name == "大卡普攻2段":
        skillParamId = "14"
    elif skill_name == "大卡普攻3段":
        skillParamId = "15"
    elif skill_name == "大卡普攻4段":
        skillParamId = "16"
    elif skill_name == "大卡普攻5段":
        skillParamId = "17"
    elif skill_name == "大卡重击":
        skillParamId = "20"
    elif skill_name == "大卡强化重击":
        skillParamId = "21"
    elif skill_name == "大卡空中1段":
        skillParamId = "25"
    elif skill_name == "大卡空中2段":
        skillParamId = "26"
    elif skill_name == "大卡空中3段":
        skillParamId = "27"
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], skillParamId, skillLevel
    )

    title = skill_name
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 风蚀效应层数 默认3层
    aeroErosionNum = 3
    if isGroup and (1406 in attr.teammate_char_ids or 1408 in attr.teammate_char_ids):
        aeroErosionNum += 3

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        # title = f"{role_name}-一链【默认吃一半】"
        # msg = "60点【决意】，暴击伤害提升25%*2"
        # attr.add_crit_dmg(0.5, title, msg)
        pass

    if chain_num >= 2:
        aeroErosionNum += 3

    if chain_num >= 3:
        pass

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "角色为目标附加【异常反应】，使队伍中所有角色全属性伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 5:
        pass

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "目标受到【芙露德莉斯】的伤害提升40%。"
        attr.add_dmg_bonus(0.4, title, msg)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 默认吃满吧
        title = f"{role_name}-以风刻痕留蚀"
        msg = "大卡对其造成的伤害提升30%；"
        attr.add_dmg_bonus(0.3, title, msg)

        aeroErosionNumTemp = min(aeroErosionNum - 3, 3)
        if aeroErosionNumTemp > 0:
            title = f"{role_name}-以风刻痕留蚀"
            msg = f"3层风蚀，对其造成的伤害额外提升10%*{aeroErosionNumTemp}"
            attr.add_dmg_bonus(0.1 * aeroErosionNumTemp, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_life = attr.effect_life
    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_life):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_life):,.0f}"
    return crit_damage, expected_damage


def calc_damage_12(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    attr.set_env_aero_erosion()
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_life")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "31", skillLevel
    )

    title = "大卡共鸣解放"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 风蚀效应层数 默认3层
    aeroErosionNum = 3
    if isGroup and (1406 in attr.teammate_char_ids or 1408 in attr.teammate_char_ids):
        aeroErosionNum += 3

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "120点【决意】，暴击伤害提升25%*4"
        attr.add_crit_dmg(1, title, msg)

    if chain_num >= 2:
        aeroErosionNum += 3

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "共鸣解放·看潮怒风哮之刃的伤害倍率提升100%"
        attr.add_skill_ratio(1, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "角色为目标附加【异常反应】，使队伍中所有角色全属性伤害加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 5:
        pass

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "目标受到【芙露德莉斯】的伤害提升40%。"
        attr.add_easy_damage(0.4, title, msg)

    # 造成伤害时目标每拥有1层【风蚀效应】，对目标造成的伤害加深20%，至多5层，命中后会清空目标拥有的【风蚀效应】。
    aeroErosionNumTemp = min(aeroErosionNum, 5)
    title = f"{role_name}-看潮怒风哮之刃"
    msg = f"{aeroErosionNumTemp}层【风蚀效应】，对目标造成的伤害加深20%*{aeroErosionNumTemp}"
    attr.add_dmg_deepen(0.2 * aeroErosionNumTemp, title, msg)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        # 默认吃满吧
        title = f"{role_name}-以风刻痕留蚀"
        msg = "大卡对其造成的伤害提升30%；"
        attr.add_dmg_bonus(0.3, title, msg)

        aeroErosionNumTemp = min(aeroErosionNum - 3, 3)
        if aeroErosionNumTemp > 0:
            title = f"{role_name}-以风刻痕留蚀"
            msg = f"3层风蚀，对其造成的伤害额外提升10%*{aeroErosionNumTemp}"
            attr.add_dmg_bonus(0.1 * aeroErosionNumTemp, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_life = attr.effect_life
    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_life):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_life):,.0f}"
    return crit_damage, expected_damage


def calc_damage_20(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_life")

    # 风主buff
    fengzhu_buff(attr, 0, 1, isGroup)

    return calc_damage_12(attr, role, isGroup)


damage_detail = [
    {
        "title": "小卡普攻3段",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_name="小卡普攻3段"),
    },
    {
        "title": "小卡普攻4段",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_name="小卡普攻4段"),
    },
    {
        "title": "小卡重击",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_name="小卡重击"),
    },
    {
        "title": "小卡空中攻击",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_name="小卡空中攻击"),
    },
    {
        "title": "3剑下落",
        "func": lambda attr, role: calc_damage_1(
            attr, role, skill_name="小卡空中回收3剑"
        ),
    },
    {
        "title": "小卡共鸣技能",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "r2",
        "func": lambda attr, role: calc_damage_12(attr, role),
    },
    {
        "title": "风主01/r2",
        "func": lambda attr, role: calc_damage_20(attr, role),
    },
]

rank = damage_detail[4]
