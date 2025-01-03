# 维里奈
from .damage import echo_damage, weapon_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import cast_skill, skill_damage_calc, heal_bonus, SkillTreeMap, SkillType, cast_attack, \
    cast_liberation, cast_hit


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(heal_bonus)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣回路"
    # 技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "5", skillLevel)
    title = "星星花绽放"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    damage_func = [cast_attack, cast_hit, cast_skill]

    # 设置角色等级
    attr.set_character_level(role_level)
    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-自然的献礼"
        msg = f"施放星星花绽放，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    chain_num = role.get_chain_num()
    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"治疗生命值低于50%的角色时，维里奈的治疗效果加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_attack)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(heal_bonus)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣解放"
    # 技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel)
    title = "草木生长"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    damage_func = [cast_attack, cast_skill, cast_liberation]

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-自然的献礼"
        msg = f"施放星星花绽放，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    chain_num = role.get_chain_num()
    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"治疗生命值低于50%的角色时，维里奈的治疗效果加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_attack)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_3(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(heal_bonus)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣解放"
    # 技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel)
    title = "协同攻击"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    damage_func = [cast_attack, cast_skill, cast_liberation]

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-自然的献礼"
        msg = f"施放星星花绽放，队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    chain_num = role.get_chain_num()
    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = f"共鸣解放光合标记的治疗效果加成提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"治疗生命值低于50%的角色时，维里奈的治疗效果加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_attack)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


damage_detail = [
    {
        "title": "星星花绽放治疗量",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "草木生长治疗量",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "协同攻击治疗量",
        "func": lambda attr, role: calc_damage_3(attr, role),
    }
]

rank = damage_detail[2]
