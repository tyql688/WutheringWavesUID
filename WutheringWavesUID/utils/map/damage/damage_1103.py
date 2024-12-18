# 白芷
from .damage import echo_damage, weapon_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import cast_skill, skill_damage_calc, heal_bonus, SkillTreeMap, SkillType, cast_attack, \
    cast_liberation


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(heal_bonus)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_life')

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣技能"
    # 技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel)
    title = "应急预案"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    damage_func = [cast_attack, cast_skill]

    # 设置角色等级
    attr.set_character_level(role_level)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二命"
        msg = f"施放共鸣技能时，满【念意】，治疗效果加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_life)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(heal_bonus)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_life')

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣解放"
    # 技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel)
    title = "刹那合弥"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    damage_func = [cast_attack, cast_skill, cast_liberation]

    # 设置角色等级
    attr.set_character_level(role_level)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二命"
        msg = f"施放共鸣技能时，满【念意】，治疗效果加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_life)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_3(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(heal_bonus)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_life')

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
    title = "频隙回响"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    damage_func = [cast_attack, cast_skill, cast_liberation]

    # 设置角色等级
    attr.set_character_level(role_level)

    attr.set_phantom_dmg_bonus(needShuxing=False)

    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二命"
        msg = f"施放共鸣技能时，满【念意】，治疗效果加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四命"
        msg = f"频隙回响治疗倍率提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_life)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


damage_detail = [
    {
        "title": "应急预案治疗量",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "刹那合弥治疗量",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "频隙回响治疗量",
        "func": lambda attr, role: calc_damage_3(attr, role),
    }
]

rank = damage_detail[2]
