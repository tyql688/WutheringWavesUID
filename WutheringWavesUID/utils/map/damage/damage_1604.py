# 暗主

from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, liberation_damage, cast_liberation, \
    cast_attack, cast_hit


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    临渊死寂
    """
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 临渊死寂 技能倍率
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    title = f"临渊死寂"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    attr.set_phantom_dmg_bonus()

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = [cast_attack, cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    if role_breach and role_breach >= 3:
        # 固有技能
        title = f"{role_name}-固有技能-变格"
        msg = "处于暗涌状态时，湮灭伤害加成提升20%。"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 4:
        # 4命
        title = f"{role_name}-四链"
        msg = "重击灭音、共鸣解放命中目标时，目标的湮灭抗性降低10%，持续20秒。"
        attr.add_enemy_resistance(-0.1, title, msg)

    if chain_num >= 6:
        # 6命
        title = f"{role_name}-六链"
        msg = "处于暗涌状态时，漂泊者的暴击提升25%。"
        attr.add_crit_rate(0.25, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "临渊死寂",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
]

rank = damage_detail[0]
