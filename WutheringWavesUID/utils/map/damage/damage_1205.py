# 长离
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...damage.abstract import WavesWeaponRegister, WavesEchoRegister
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage, SONATA_MOLTEN, check_if_ph_5


def calc_damage_0(attr: DamageAttribute, role: RoleDetailData) -> (str, str):
    """
    焚身以火
    """
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 焚身以火 技能倍率
    skillLevel = role.skillList[4].level - 1
    # 技能倍率
    skill_multi = skill_damage(char_result.skillTrees, "7", "1", skillLevel)
    attr.set_skill_multi(skill_multi)

    # 设置角色等级
    attr.set_character_level(role_level)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MOLTEN):
            # 热熔声骸五件套
            attr.add_dmg_bonus(0.3)

    if role_breach >= 3:
        # 固2(散势) 0.2
        attr.add_dmg_bonus(0.2)
        attr.add_defense_reduction(0.15)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.skill_damage:
        # 共鸣技能伤害 ->  来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.skill_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 1:
        # 1命
        attr.add_dmg_bonus(0.1)

    if chain_num >= 2:
        # 2命
        attr.add_crit_rate(0.25)

    if chain_num >= 4:
        # 4命
        attr.add_atk_percent(0.2)

    if chain_num >= 5:
        # 5命
        attr.add_skill_ratio(0.5)
        attr.add_dmg_bonus(0.5)

    if chain_num >= 6:
        # 6命
        attr.add_defense_reduction(0.4)

    # 声骸技能
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo('liberation_damage', attr)

    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(role.weaponData.weapon.weaponId)
    if weapon_clz:
        weapon_data = role.weaponData
        w = weapon_clz(weapon_data.weapon.weaponId,
                       weapon_data.level,
                       weapon_data.breach,
                       weapon_data.resonLevel)
        w.do_action('skill_damage', attr)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData) -> (str, str):
    """
    离火照丹心
    """
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 离火照丹心 技能倍率
    skillLevel = role.skillList[2].level - 1
    # 技能倍率
    skill_multi = skill_damage(char_result.skillTrees, "3", "1", skillLevel)
    attr.set_skill_multi(skill_multi)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MOLTEN):
            # 热熔声骸五件套
            attr.add_dmg_bonus(0.3)

    # 设置角色等级
    attr.set_character_level(role_level)

    if role_breach >= 3:
        # 固2(散势) 0.2
        attr.add_dmg_bonus(0.2)
        attr.add_defense_reduction(0.15)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.liberation_damage:
        # 共鸣解放伤害 ->  来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.liberation_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 2:
        # 2命
        attr.add_crit_rate(0.25)

    if chain_num >= 3:
        # 3命
        attr.add_dmg_bonus(0.8)

    if chain_num >= 4:
        # 4命
        attr.add_atk_percent(0.2)

    if chain_num >= 6:
        # 6命
        attr.add_defense_reduction(0.4)

    # 声骸技能
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo('liberation_damage', attr)

    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(role.weaponData.weapon.weaponId)
    if weapon_clz:
        weapon_data = role.weaponData
        w = weapon_clz(weapon_data.weapon.weaponId,
                       weapon_data.level,
                       weapon_data.breach,
                       weapon_data.resonLevel)
        w.do_action('liberation_damage', attr)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "焚身以火",
        "func": lambda attr, role: calc_damage_0(attr, role),
    },
    {
        "title": "离火照丹心",
        "func": lambda attr, role: calc_damage_1(attr, role),
    }
]
