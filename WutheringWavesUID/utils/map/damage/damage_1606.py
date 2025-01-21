# 洛可可
from .buff import shouanren_buff, motefei_buff
from .damage import echo_damage, phase_damage, weapon_damage
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillType,
    SkillTreeMap,
    cast_hit,
    cast_skill,
    hit_damage,
    cast_attack,
    cast_liberation,
    skill_damage_calc,
)


def calc_damage_0(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    title = "默认手法"
    if isGroup:
        msg = "变奏入场 a qr e aaa"
    else:
        msg = "z qr e aaa"
    attr.add_effect(title, msg)
    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    # 获取角色详细信息
    char_result = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi1 = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    skill_multi2 = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )
    skill_multi3 = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能"
        msg = f"施放共鸣技能或重击时，洛可可攻击提升20%，持续12秒。"
        attr.add_atk_percent(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"施放普攻幻想照进现实时，湮灭伤害加成提升10%*3。满层时，湮灭伤害加成额外提升10%"
        attr.add_effect(title, msg)
        # attr.add_dmg_bonus(0.4, title, msg)

    if isGroup and chain_num >= 3:
        title = f"{role_name}-三链"
        msg = f"施放变奏技能时，洛可可暴击提升10%，暴击伤害提升30%"
        attr.add_effect(title, msg)
        attr.add_crit_rate(0.1, title, msg)
        attr.add_crit_dmg(0.3, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"施放共鸣技能高难度设计时，普攻幻想照进现实伤害倍率提升60%"
        attr.add_skill_ratio(0.6, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"普攻幻想照进现实攻击目标时，无视对方60%的防御。"
        attr.add_defense_reduction(0.6, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 洛可可暴击高于50%时，每多出0.1%暴击，施放该技能时，使队伍中的角色攻击提升1点，持续30秒。最高可提升200点
    crit_rate_overflow = attr.crit_rate - 0.5
    if crit_rate_overflow > 0:
        atk_flat = int(crit_rate_overflow * 1000)
        atk_flat = min(atk_flat, 200)

        title = f"{role_name}-暴击提升攻击值"
        msg = f"暴击最高可提升200点攻击，当前提升{atk_flat}点"
        attr.add_atk_flat(atk_flat, title, msg)

    title = "普攻·幻想照进现实-第{}段倍率"
    title2 = "第{}段伤害"
    msg = "技能倍率{}"
    if chain_num >= 2:
        attr.add_dmg_bonus(0.1)
    attr.add_effect(title.format(1), msg.format(skill_multi1))
    attr.set_skill_multi(skill_multi1)
    crit_damage1 = attr.calculate_crit_damage()
    expected_damage1 = attr.calculate_expected_damage()
    attr.add_effect(
        title2.format(1),
        f"期望伤害:{crit_damage1:,.0f}; 暴击伤害:{expected_damage1:,.0f}",
    )
    if chain_num >= 2:
        attr.add_dmg_bonus(0.1)
    attr.add_effect(title.format(2), msg.format(skill_multi2))
    attr.set_skill_multi(skill_multi2)
    crit_damage2 = attr.calculate_crit_damage()
    expected_damage2 = attr.calculate_expected_damage()
    attr.add_effect(
        title2.format(2),
        f"期望伤害:{crit_damage2:,.0f}; 暴击伤害:{expected_damage2:,.0f}",
    )

    if chain_num >= 2:
        attr.add_dmg_bonus(0.2)
    attr.add_effect(title.format(3), msg.format(skill_multi3))
    attr.set_skill_multi(skill_multi3)
    crit_damage3 = attr.calculate_crit_damage()
    expected_damage3 = attr.calculate_expected_damage()
    attr.add_effect(
        title2.format(3),
        f"期望伤害:{crit_damage3:,.0f}; 暴击伤害:{expected_damage3:,.0f}",
    )

    crit_damage = crit_damage1 + crit_damage2 + crit_damage3
    expected_damage = expected_damage1 + expected_damage2 + expected_damage3

    # 暴击伤害
    crit_damage = f"{crit_damage:,.0f}"
    # 期望伤害
    expected_damage = f"{expected_damage:,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    title = "默认手法"
    if isGroup:
        msg = "变奏入场 a qr e aaa"
    else:
        msg = "z qr e aaa"
    attr.add_effect(title, msg)
    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    # 获取角色详细信息
    char_result = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )
    title = f"普攻·幻想照进现实-第三段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能"
        msg = f"施放共鸣技能或重击时，洛可可攻击提升20%，持续12秒。"
        attr.add_atk_percent(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"队伍中的角色湮灭伤害加成提升10%*4"
        attr.add_dmg_bonus(0.4, title, msg)

    if isGroup and chain_num >= 3:
        title = f"{role_name}-三链"
        msg = f"施放变奏技能时，洛可可暴击提升10%，暴击伤害提升30%"
        attr.add_effect(title, msg)
        attr.add_crit_rate(0.1)
        attr.add_crit_dmg(0.3)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"施放共鸣技能高难度设计时，普攻幻想照进现实伤害倍率提升60%"
        attr.add_skill_ratio(0.6, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"普攻幻想照进现实攻击目标时，无视对方60%的防御。"
        attr.add_defense_reduction(0.6, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 洛可可暴击高于50%时，每多出0.1%暴击，施放该技能时，使队伍中的角色攻击提升1点，持续30秒。最高可提升200点
    crit_rate_overflow = attr.crit_rate - 0.5
    if crit_rate_overflow > 0:
        atk_flat = int(crit_rate_overflow * 1000)
        atk_flat = min(atk_flat, 200)

        title = f"{role_name}-暴击提升攻击值"
        msg = f"暴击最高可提升200点攻击，当前提升{atk_flat}点"
        attr.add_atk_flat(atk_flat, title, msg)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_3(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    title = "默认手法"
    if isGroup:
        msg = "变奏入场 a e aaa qr"
    else:
        msg = "z e aaa qr"
    attr.add_effect(title, msg)
    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    # 获取角色详细信息
    char_result = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = f"即兴喜剧开场"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能"
        msg = f"施放共鸣技能或重击时，洛可可攻击提升20%，持续12秒。"
        attr.add_atk_percent(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"队伍中的角色湮灭伤害加成提升10%*4"
        attr.add_dmg_bonus(0.4, title, msg)

    if isGroup and chain_num >= 3:
        title = f"{role_name}-三链"
        msg = f"施放变奏技能时，洛可可暴击提升10%，暴击伤害提升30%"
        attr.add_effect(title, msg)
        attr.add_crit_rate(0.1)
        attr.add_crit_dmg(0.3)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"共鸣解放即兴喜剧，开场伤害倍率提升20%，重击伤害倍率提升80%。"
        attr.add_skill_ratio(0.2)
        attr.add_dmg_deepen(0.8)
        attr.add_effect(title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 洛可可暴击高于50%时，每多出0.1%暴击，施放该技能时，使队伍中的角色攻击提升1点，持续30秒。最高可提升200点
    crit_rate_overflow = attr.crit_rate - 0.5
    if crit_rate_overflow > 0:
        atk_flat = int(crit_rate_overflow * 1000)
        atk_flat = min(atk_flat, 200)

        title = f"{role_name}-暴击提升攻击值"
        msg = f"暴击最高可提升200点攻击，当前提升{atk_flat}点"
        attr.add_atk_flat(atk_flat, title, msg)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_10(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> (str, str):
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 6, 5, isGroup)

    # 莫特斐buff
    motefei_buff(attr, 6, 5, isGroup)

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "强化a尾刀伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "强化a三段总伤害",
        "func": lambda attr, role: calc_damage_0(attr, role),
    },
    {
        "title": "即兴喜剧伤害",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "6+5守/6+5莫/强化a尾刀伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    },
]

rank = damage_detail[0]
