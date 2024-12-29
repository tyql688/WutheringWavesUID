# 珂莱塔
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, SkillType, SkillTreeMap, cast_skill, cast_attack, \
    cast_hit, skill_damage, cast_liberation


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa qz"
    else:
        msg = "ee aa aaa qz"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel)
    title = f"末路见行"
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
        title = f"{role_name}-固有技能-艺术至上"
        msg = f"为命中的目标附加解离效果"
        attr.add_effect(title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一命"
        msg = f"对拥有解离效果的目标攻击造成伤害时，该次伤害的暴击提升12.5%"
        attr.add_crit_rate(0.125, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四命"
        msg = f"珂莱塔施放重击末路见行时，队伍中的角色共鸣技能伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五命"
        msg = f"重击末路见行的伤害倍率提升47%"
        attr.add_skill_ratio(0.47, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    title = "默认手法"
    if isGroup:
        msg = "变奏入场 ee aa aaa z qr aaaaa"
    else:
        msg = "ee aa aaa z qr aaaaa"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel)
    title = f"致死以终"
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
        title = f"{role_name}-固有技能-艺术至上"
        msg = f"为命中的目标附加解离效果"
        attr.add_effect(title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    title = f"{role_name}-解离状态"
    msg = f"造成伤害时忽视目标18%防御"
    attr.add_defense_reduction(0.18, title, msg)

    title = f"{role_name}-揭幕者状态"
    msg = f"共鸣解放致死以终的伤害倍率提升80%"
    attr.add_skill_ratio(0.8, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一命"
        msg = f"对拥有解离效果的目标攻击造成伤害时，该次伤害的暴击提升12.5%"
        attr.add_crit_rate(0.125, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二命"
        msg = f"共鸣解放致死以终的伤害倍率提升126%"
        attr.add_skill_ratio(1.26, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四命"
        msg = f"珂莱塔施放重击末路见行时，队伍中的角色共鸣技能伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "末路见行伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "致死以终伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    }
]

rank = damage_detail[1]
