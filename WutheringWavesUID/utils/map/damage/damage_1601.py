# 桃祈

from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, SkillType, SkillTreeMap, cast_skill, cast_attack, \
    cast_hit, attack_damage, cast_liberation, liberation_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False,
                  isHitCounterattack: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_def')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "9", skillLevel)
    title = f"御反之隙第一段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "10", skillLevel)
    title = f"御反之隙第二段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "11", skillLevel)
    title = f"御反之隙第三段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能"
        msg = f"共鸣技能磐岩护壁持续期间，角色的防御提升15%。"
        attr.add_def_percent(0.15, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 4 and isHitCounterattack:
        title = f"{role_name}-四链"
        msg = f"成功触发重击后发制人时，防御提升50%"
        attr.add_def_percent(0.5, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"共鸣回路攻防转换的伤害提升50%"
        attr.add_dmg_bonus(0.5, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"共鸣技能磐岩护壁获得的护盾持续期间，桃祈普攻伤害提升40%"
        attr.add_dmg_bonus(0.4, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_value = attr.effect_def
    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_value):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_value):,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False,
                  isHitCounterattack: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_def')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "20", skillLevel)
    title = f"不动如山"
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
        msg = f"共鸣技能磐岩护壁持续期间，角色的防御提升15%。"
        attr.add_def_percent(0.15, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"共鸣解放不动如山的暴击提升20%，暴击伤害提升20%。"
        attr.add_crit_rate(0.2)
        attr.add_crit_dmg(0.2)
        attr.add_effect(title, msg)

    if chain_num >= 4 and isHitCounterattack:
        title = f"{role_name}-四链"
        msg = f"成功触发重击后发制人时，防御提升50%"
        attr.add_def_percent(0.5, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    effect_value = attr.effect_def
    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage(effect_value):,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage(effect_value):,.0f}"
    return crit_damage, expected_damage


def calc_damage_3(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False,
                  isHitCounterattack: bool = False) -> (str, str):
    damage_func = [cast_attack, cast_skill, cast_hit]
    attr.set_char_damage("")
    attr.set_char_template('temp_def')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)
    # 技能等级
    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "27", skillLevel)
    title = f"御反之隙第一段护盾"
    msg = f"技能倍率{skill_multi}"
    attr.add_shield_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "28", skillLevel)
    title = f"御反之隙第二段护盾"
    msg = f"技能倍率{skill_multi}"
    attr.add_shield_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "29", skillLevel)
    title = f"御反之隙第三段护盾"
    msg = f"技能倍率{skill_multi}"
    attr.add_shield_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能"
        msg = f"共鸣技能磐岩护壁持续期间，角色的防御提升15%。"
        attr.add_def_percent(0.15, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus(needPhantom=False, needShuxing=False)

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 4 and isHitCounterattack:
        title = f"{role_name}-四链"
        msg = f"成功触发重击后发制人时，防御提升50%"
        attr.add_def_percent(0.5, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    shield_bonus = attr.calculate_shield(attr.effect_def)

    crit_damage = f"{shield_bonus:,.0f}"
    return None, crit_damage


damage_detail = [
    {
        "title": "御反之隙总伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "重反-御反之隙总伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, isHitCounterattack=True),
    },
    {
        "title": "不动如山",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "重反-不动如山",
        "func": lambda attr, role: calc_damage_2(attr, role, isHitCounterattack=True),
    },
    {
        "title": "御反之隙总护盾量",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "重反-御反之隙总护盾量",
        "func": lambda attr, role: calc_damage_3(attr, role, isHitCounterattack=True),
    },
]

rank = damage_detail[5]
