# 仇远


from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_phantom,
    cast_skill,
    hit_damage,
    phantom_damage,
    skill_damage_calc,
)
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "27", skillLevel
    )
    title = "答剑·忠烈死节"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation, cast_phantom]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = "固有技能-与尔同销万古愁"
        msg = "仇远攻击提升10%"
        attr.add_atk_percent(0.1, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "暴击提升20%"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "答剑·忠烈死节伤害倍率增加600%"
        attr.add_skill_multi(6, title, msg)
    else:
        title = "固有技能-且从容"
        msg = "伤害提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "无视目标15%的防御"
        attr.add_defense_reduction(0.15, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "施放共鸣技能荷蓑出林时，仇远暴击伤害增加100%"
        attr.add_crit_dmg(1, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 仇远暴击高于50%时，每多出1%暴击，施放该技能时，附近队伍中的登场角色提升2%暴击伤害，持续30秒。最高可提升30%暴击伤害。
    crit_rate = attr.crit_rate
    if crit_rate > 0.5:
        crit_rate = crit_rate - 0.5
        crit_rate_bonus = int(min(max(crit_rate / 0.01, 0), 15))
        print(crit_rate_bonus)
        title = "共鸣解放"
        msg = f"暴击伤害提升2*{crit_rate_bonus}%"
        attr.add_crit_dmg(crit_rate_bonus * 0.02, title, msg)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(phantom_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "13", skillLevel
    )
    title = "万钧一断"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation, cast_phantom]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = "固有技能-与尔同销万古愁"
        msg = "仇远攻击提升10%"
        attr.add_atk_percent(0.1, title, msg)
    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 竹照
    # 获得【竹照】效果，附近队伍中的登场角色声骸技能伤害加成提升30%，持续30秒。
    title = "竹照"
    msg = "声骸技能伤害加成提升30%"
    attr.add_dmg_bonus(0.3, title, msg)

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "暴击提升20%"
        attr.add_crit_rate(0.2, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "【竹照】：附近队伍中的角色声骸技能伤害加深30%。"
        attr.add_dmg_deepen(0.3, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "共鸣解放万钧一断伤害倍率增加500%"
        attr.add_skill_multi(5, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "无视目标15%的防御"
        attr.add_defense_reduction(0.15, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "施放共鸣技能荷蓑出林时，仇远暴击伤害增加100%"
        attr.add_crit_dmg(1, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 仇远暴击高于50%时，每多出1%暴击，施放该技能时，附近队伍中的登场角色提升2%暴击伤害，持续30秒。最高可提升30%暴击伤害。
    crit_rate = attr.crit_rate
    if crit_rate > 0.5:
        crit_rate = crit_rate - 0.5
        crit_rate_bonus = int(min(max(crit_rate / 0.01, 0), 15))
        title = "共鸣解放"
        msg = f"暴击伤害提升2*{crit_rate_bonus}%"
        attr.add_crit_dmg(crit_rate_bonus * 0.02, title, msg)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "答剑·忠烈死节",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "万钧一断",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
]

rank = damage_detail[0]
