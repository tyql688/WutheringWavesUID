# 秧秧
from .buff import shouanren_buff, changli_buff
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, SkillType, SkillTreeMap, cast_skill, cast_attack, \
    cast_hit, attack_damage, liberation_damage, cast_liberation


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel)
    title = f"空中攻击·释羽"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-怀悯"
            msg = f"施放变奏技能后，气动伤害加成提升8%"
            attr.add_dmg_bonus(0.08, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        if isGroup:
            title = f"{role_name}-一链"
            msg = f"施放变奏技能后，秧秧的气动伤害加成额外提升15%"
            attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = f"空中攻击释羽的伤害提升95%。"
        attr.add_dmg_bonus(0.95, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"施放空中攻击释羽后，队伍中的角色的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel)
    title = f"朔风旋涌"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-怀悯"
            msg = f"施放变奏技能后，气动伤害加成提升8%"
            attr.add_dmg_bonus(0.08, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        if isGroup:
            title = f"{role_name}-一链"
            msg = f"施放变奏技能后，秧秧的气动伤害加成额外提升15%"
            attr.add_dmg_bonus(0.15, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"共鸣解放朔风旋涌的伤害提升85%。"
        attr.add_dmg_bonus(0.85, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"施放空中攻击释羽后，队伍中的角色的攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_10(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True) -> (str, str):
    attr.set_char_damage(liberation_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 长离buff
    changli_buff(attr, 0, 1, isGroup)

    return calc_damage_2(attr, role, isGroup)


damage_detail = [
    {
        "title": "空中攻击·释羽",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "朔风旋涌r伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "0+1守/0+0长离/r伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    }
]

rank = damage_detail[2]
