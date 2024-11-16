# 椿
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.abstract import WavesWeaponRegister, WavesEchoRegister
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage, check_if_ph_5, SONATA_SINKING


def calc_damage_0(attr: DamageAttribute, role: RoleDetailData) -> (str, str):
    is_group = False

    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 一日花 技能倍率
    # 回路倍率 = 4
    skillLevel = role.skillList[4].level - 1
    # 技能倍率 回路技能树 "7"
    skill_multi = skill_damage(char_result.skillTrees, "7", "1", skillLevel)
    attr.set_skill_multi(skill_multi)

    # 设置角色等级
    attr.set_character_level(role_level)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SINKING):
            # 湮灭声骸五件套
            attr.add_dmg_bonus(0.3)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.attack_damage:
        # 普攻伤害加成 ->  来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.attack_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 1 and is_group:
        # 1命
        # 变奏入场
        attr.add_crit_dmg(0.28)

    if chain_num >= 2:
        # 2命
        attr.add_skill_ratio(1.2)

    if chain_num >= 3:
        # 3命
        attr.add_atk_percent(0.58)

    if chain_num >= 4 and is_group:
        # 4命
        # 变奏入场
        attr.add_dmg_bonus(0.25)

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
        w.do_action('attack_damage', attr)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData) -> (str, str):
    """
    芳华绽烬
    """
    is_group = False
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 芳华绽烬 技能倍率
    skillLevel = role.skillList[2].level - 1
    # 技能倍率
    skill_multi = skill_damage(char_result.skillTrees, "3", "1", skillLevel)
    attr.set_skill_multi(skill_multi)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SINKING):
            # 湮灭声骸五件套
            attr.add_dmg_bonus(0.3)

    # 设置角色等级
    attr.set_character_level(role_level)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.liberation_damage:
        # 共鸣解放伤害 ->  来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.liberation_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 1 and is_group:
        # 1命
        # 变奏入场
        attr.add_crit_dmg(0.28)

    if chain_num >= 3:
        # 3命
        attr.add_skill_ratio(0.5)

    if chain_num >= 4 and is_group:
        # 4命
        # 变奏入场
        attr.add_dmg_bonus(0.25)

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
        "title": "一日花",
        "func": lambda attr, role: calc_damage_0(attr, role),
    },
    {
        "title": "芳华绽烬",
        "func": lambda attr, role: calc_damage_1(attr, role),
    }
]
