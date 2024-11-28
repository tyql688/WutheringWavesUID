# 椿
from .buff import sanhua_buff, shouanren_buff
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, attack_damage, cast_attack, \
    liberation_damage, cast_liberation


def calc_damage_0(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    一日花
    """
    attr.set_char_damage(attack_damage)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 一日花 技能倍率
    # 回路倍率 = 4
    skillLevel = role.skillList[4].level - 1
    # 技能倍率 回路技能树 "7"
    skill_multi = skill_damage_calc(char_result.skillTrees, "7", "1", skillLevel)
    title = f"{role_name}-一日花技能倍率"
    msg = f"{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = cast_attack
    phase_damage(attr, role, damage_func, isGroup)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()
    if chain_num >= 1 and isGroup:
        # 1命
        # 变奏入场
        title = f"{role_name}-一命"
        msg = f"施放变奏技能八千春秋时，暴击伤害提升28%"
        attr.add_crit_dmg(0.28, title, msg)

    if chain_num >= 2:
        # 2命
        title = f"{role_name}-二命"
        msg = f"共鸣回路一日花伤害倍率提升120%"
        attr.add_skill_ratio(1.2, title, msg)

    if chain_num >= 3:
        # 3命
        title = f"{role_name}-三命"
        msg = f"含苞状态期间，椿的攻击提升58%。"
        attr.add_atk_percent(0.58, title, msg)

    if chain_num >= 4 and isGroup:
        # 4命
        title = f"{role_name}-四命"
        msg = f"变奏技能八千春秋后，队伍中的角色普攻伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    芳华绽烬
    """
    attr.set_char_damage(liberation_damage)

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 芳华绽烬 技能倍率
    skillLevel = role.skillList[2].level - 1
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    attr.add_skill_multi(skill_multi)

    damage_func = [cast_attack, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role_level)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()
    if chain_num >= 1 and isGroup:
        # 1命
        # 变奏入场
        title = f"{role_name}-一命"
        msg = f"施放变奏技能八千春秋时，暴击伤害提升28%"
        attr.add_crit_dmg(0.28, title, msg)

    if chain_num >= 3:
        # 3命
        title = f"{role_name}-三命"
        msg = f"共鸣解放芳华绽烬伤害倍率提升50%；含苞状态期间，椿的攻击提升58%。"
        attr.add_atk_percent(0.58)
        attr.add_skill_ratio(0.5)
        attr.add_effect(title, msg)

    if chain_num >= 4 and isGroup:
        # 4命
        # 变奏入场
        title = f"{role_name}-四命"
        msg = f"变奏技能八千春秋后，队伍中的角色普攻伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True) -> (str, str):
    attr.set_char_damage(attack_damage)
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 散华buff
    sanhua_buff(attr, 6, 1, isGroup)

    return calc_damage_0(attr, role, isGroup)


damage_detail = [
    {
        "title": "一日花",
        "func": lambda attr, role: calc_damage_0(attr, role),
    },
    {
        "title": "芳华绽烬",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "0+1守/6散/一日花",
        "func": lambda attr, role: calc_damage_2(attr, role),
    }
]

rank = damage_detail[0]
