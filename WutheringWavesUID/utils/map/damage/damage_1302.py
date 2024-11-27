# 吟霖
from .damage import weapon_damage, echo_damage
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...ascension.sonata import get_sonata_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import check_if_ph_5, SONATA_VOID, skill_damage_calc, skill_damage, cast_skill, liberation_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    审判之雷
    """
    damage_func = [cast_skill]
    attr.set_char_damage(skill_damage)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 审判之雷 技能倍率
    skillLevel = role.get_skill_level("共鸣回路")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "7", "20", skillLevel)
    title = "审判之雷"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置协同攻击
    attr.set_sync_strike()

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_VOID):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-浸渍痛楚"
        msg = f"使用共鸣技能磁殛咆哮后，暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()

    if chain_num >= 3:
        # 3命
        title = f"{role_name}-三命"
        msg = f"共鸣回路审判之雷伤害倍率提升55%。"
        attr.add_skill_ratio(0.55, title, msg)

    if chain_num >= 4:
        # 4命
        title = f"{role_name}-四命"
        msg = f"共鸣回路审判之雷命中时，队伍中的角色攻击提升20%."
        attr.add_atk_percent(0.2, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    破天雷灭击
    """
    damage_func = [cast_skill]
    attr.set_char_damage(liberation_damage)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 审判之雷 技能倍率
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "15", skillLevel)
    title = "破天雷灭击"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_VOID):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-浸渍痛楚"
        msg = f"使用共鸣技能磁殛咆哮后，暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

        title = f"{role_name}-固有技能-目标专注"
        msg = f"共鸣技能召雷磁爆命中带有缚罪标记的目标，触发该效果时攻击提升10%"
        attr.add_atk_percent(0.1, title, msg)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()

    if chain_num >= 4:
        # 4命
        title = f"{role_name}-四命"
        msg = f"共鸣回路审判之雷命中时，队伍中的角色攻击提升20%."
        attr.add_atk_percent(0.2, title, msg)

    if chain_num >= 5:
        # 5命
        title = f"{role_name}-五命"
        msg = f"共鸣解放命中带有共鸣回路缚罪标记、惩罚印记的目标时，伤害提升100%。"
        attr.add_dmg_bonus(1, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "审判之雷",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "破天雷灭击",
        "func": lambda attr, role: calc_damage_2(attr, role),
    }
]
