# 守岸人
from .damage import echo_damage, weapon_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...ascension.sonata import get_sonata_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import cast_skill, skill_damage_calc, heal_bonus, cast_variation, liberation_damage, check_if_ph_5, \
    SONATA_CELESTIAL


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    damage_func = [cast_skill]
    attr.set_char_damage(heal_bonus)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 技能等级
    skillLevel = role.get_skill_level("共鸣技能")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "2", "2", skillLevel)
    title = "混沌理论"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.heal_bonus:
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.heal_bonus)

    chain_num = role.get_chain_num()
    if chain_num >= 4:
        title = f"{role_name}-四命"
        msg = f"施放共鸣技能混沌理论时，治疗效果加成提升70%。"
        attr.add_dmg_bonus(0.7, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_life)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    damage_func = [cast_skill]
    attr.set_char_damage(heal_bonus)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 技能等级
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    title = "终末回环"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.heal_bonus:
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.heal_bonus)

    chain_num = role.get_chain_num()
    if chain_num >= 4:
        title = f"{role_name}-四命"
        msg = f"施放共鸣技能混沌理论时，治疗效果加成提升70%。"
        attr.add_dmg_bonus(0.7, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    healing_bonus = attr.calculate_healing(attr.effect_life)

    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_3(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True) -> (str, str):
    damage_func = [cast_variation]
    attr.set_char_damage(liberation_damage)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 技能等级
    skillLevel = role.get_skill_level("变奏技能")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "6", "2", skillLevel)
    title = "洞悉伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    for ph_detail in attr.ph_detail:
        if isGroup and check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_CELESTIAL):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    title = "守岸人-共鸣解放"
    msg = "暴击提升12.5%+暴击伤害提升25%"
    attr.add_crit_rate(0.125)
    attr.add_crit_dmg(0.25)
    attr.add_effect(title, msg)

    title = "守岸人-延奏技能"
    msg = "队伍中的角色全伤害加深15%"
    attr.add_dmg_deepen(0.15, title, msg)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.liberation_damage:
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.liberation_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"洞悉伤害倍率提升42%。守岸人的暴击伤害提升500%。"
        attr.add_skill_ratio(0.42, title, msg)
        attr.add_crit_dmg(5)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    crit_damage = f"{attr.calculate_crit_damage(attr.effect_life):,.0f}"
    return None, crit_damage


damage_detail = [
    {
        "title": "混沌理论治疗量",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "终末回环治疗量",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "洞悉伤害",
        "func": lambda attr, role: calc_damage_3(attr, role),
    }
]
