# 暗主

from .damage import echo_damage, weapon_damage
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...ascension.sonata import get_sonata_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage, check_if_ph_5, SONATA_SINKING


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    临渊死寂
    """
    damage_func = ["liberation_damage"]

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 临渊死寂 技能倍率
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage(char_result.skillTrees, "3", "1", skillLevel)
    title = f"临渊死寂"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.liberation_damage:
        # 来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.liberation_damage)

    # 设置角色等级
    attr.set_character_level(role_level)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SINKING):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

    if role_breach >= 3:
        # 固有技能
        title = f"{role_name}-固有技能-变格"
        msg = "处于暗涌状态时，湮灭伤害加成提升20%。"
        attr.add_dmg_bonus(0.2, title, msg)

    # if chain_num >= 4:
    #     # 4命
    #     title = f"{role_name}-四命"
    #     msg = "重击灭音、共鸣解放命中目标时，目标的湮灭抗性降低10%，持续20秒。"
    #     attr.add_enemy_resistance(0.10, title, msg)
    #
    # if chain_num >= 5 and 'attack_damage' in damage_func:
    #     # 5命
    #     title = f"{role_name}-五命"
    #     msg = "处于暗涌状态时第5段普攻可额外造成一次湮灭伤害，此次伤害为第5段普攻伤害的50%。"
    #
    # if chain_num >= 6:
    #     # 6命
    #     title = f"{role_name}-六命"
    #     msg = "处于暗涌状态时，漂泊者的暴击提升25%。"
    #     attr.add_crit_rate(0.2, title, msg)

    echo_damage(attr, damage_func, isGroup)

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
