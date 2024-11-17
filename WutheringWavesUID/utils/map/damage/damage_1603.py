# 椿
from .buff import sanhua_buff, shouanren_buff
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.abstract import WavesWeaponRegister, WavesEchoRegister
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage, check_if_ph_5, SONATA_SINKING


def calc_damage_0(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    一日花
    """
    damage_func = "attack_damage"

    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 一日花 技能倍率
    # 回路倍率 = 4
    skillLevel = role.skillList[4].level - 1
    # 技能倍率 回路技能树 "7"
    skill_multi = skill_damage(char_result.skillTrees, "7", "1", skillLevel)
    title = "椿-一日花技能倍率"
    msg = f"{skill_multi}"
    attr.set_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SINKING):
            # 湮灭声骸五件套
            title = "椿-沉日劫明"
            msg = f"湮灭伤害提升7.5%，该效果可叠加四层"
            attr.add_dmg_bonus(0.3, title, msg)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.attack_damage:
        # 普攻伤害加成 -> 来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.attack_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 1 and isGroup:
        # 1命
        # 变奏入场
        title = "椿-一命"
        msg = f"施放变奏技能八千春秋时，暴击伤害提升28%"
        attr.add_crit_dmg(0.28, title, msg)

    if chain_num >= 2:
        # 2命
        title = "椿-二命"
        msg = f"共鸣回路一日花伤害倍率提升120%"
        attr.add_skill_ratio(1.2, title, msg)

    if chain_num >= 3:
        # 3命
        title = "椿-三命"
        msg = f"含苞状态期间，椿的攻击提升58%。"
        attr.add_atk_percent(0.58, title, msg)

    if chain_num >= 4 and isGroup:
        # 4命
        title = "椿-四命"
        msg = f"变奏技能八千春秋后，队伍中的角色普攻伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 声骸技能
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo(damage_func, attr)

    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(role.weaponData.weapon.weaponId)
    if weapon_clz:
        weapon_data = role.weaponData
        w = weapon_clz(weapon_data.weapon.weaponId,
                       weapon_data.level,
                       weapon_data.breach,
                       weapon_data.resonLevel)
        w.do_action(damage_func, attr)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    芳华绽烬
    """
    damage_func = "liberation_damage"

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
            title = "椿-沉日劫明"
            msg = f"湮灭伤害提升7.5%，该效果可叠加四层"
            attr.add_dmg_bonus(0.3, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.liberation_damage:
        # 共鸣解放伤害 ->  来自声骸
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.liberation_damage)

    chain_num = role.get_chain_num()
    if chain_num >= 1 and isGroup:
        # 1命
        # 变奏入场
        title = "椿-一命"
        msg = f"施放变奏技能八千春秋时，暴击伤害提升28%"
        attr.add_crit_dmg(0.28, title, msg)

    if chain_num >= 3:
        # 3命
        title = "椿-三命"
        msg = f"共鸣解放芳华绽烬伤害倍率提升50%；含苞状态期间，椿的攻击提升58%。"
        attr.add_atk_percent(0.58)
        attr.add_skill_ratio(0.5)
        attr.add_effect(title, msg)

    if chain_num >= 4 and isGroup:
        # 4命
        # 变奏入场
        title = "椿-四命"
        msg = f"变奏技能八千春秋后，队伍中的角色普攻伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 声骸技能
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo(damage_func, attr)

    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(role.weaponData.weapon.weaponId)
    if weapon_clz:
        weapon_data = role.weaponData
        w = weapon_clz(weapon_data.weapon.weaponId,
                       weapon_data.level,
                       weapon_data.breach,
                       weapon_data.resonLevel)
        w.do_action(damage_func, attr)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True) -> (str, str):
    damage_func = "attack_damage"

    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup, damage_func)

    # 散华buff
    sanhua_buff(attr, 6, 1, isGroup, damage_func)

    return calc_damage_0(attr, role, isGroup)


damage_detail = [
    {
        "id": 1,
        "title": "一日花",
        "func": lambda attr, role: calc_damage_0(attr, role),
    },
    {
        "id": 2,
        "title": "芳华绽烬",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "id": 3,
        "title": "0+1守6散一日花",
        "func": lambda attr, role: calc_damage_2(attr, role),
    }
]
