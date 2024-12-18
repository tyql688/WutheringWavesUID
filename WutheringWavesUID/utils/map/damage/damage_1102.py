# 散华
from .buff import shouanren_buff, changli_buff
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, SkillType, SkillTreeMap, skill_damage, cast_skill, cast_attack, \
    liberation_damage, cast_liberation, hit_damage, cast_hit


def calc_damage_0(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel)
    title = f"重击·爆裂"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一命"
        msg = f"施放第5段普攻时，散华自身暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"散华攻击生命低于70%的目标时，造成的伤害提升35%。"
        attr.add_dmg_bonus(0.35, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四命"
        msg = f"施放共鸣解放时，下次重击爆裂伤害提升120%"
        attr.add_dmg_bonus(1.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"引爆【冰棱】或【冰川】后，队伍中的角色攻击提升10%*2"
        attr.add_atk_percent(0.1, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣技能"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel)
    title = f"冰棱伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-凝冰"
            msg = f"施放变奏技能时，散华的共鸣技能伤害提升20%"
            attr.add_dmg_bonus(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一命"
        msg = f"施放第5段普攻时，散华自身暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"散华攻击生命低于70%的目标时，造成的伤害提升35%。"
        attr.add_dmg_bonus(0.35, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"引爆【冰棱】或【冰川】后，队伍中的角色攻击提升10%*2"
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
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel)
    title = f"冰棱爆炸伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-凝冰"
            msg = f"施放变奏技能时，散华的共鸣技能伤害提升20%"
            attr.add_dmg_bonus(0.2, title, msg)

        title = f"{role_name}-固有技能-瀑雪"
        msg = "施放第5段普攻后，冰绽造成的伤害提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一命"
        msg = f"施放第5段普攻时，散华自身暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"散华攻击生命低于70%的目标时，造成的伤害提升35%。"
        attr.add_dmg_bonus(0.35, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五命"
        msg = "冰绽的暴击伤害提升100%。"
        attr.add_crit_dmg(1, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"引爆【冰棱】或【冰川】后，队伍中的角色攻击提升10%*2"
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


def calc_damage_3(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
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
    title = f"冰川伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一命"
        msg = f"施放第5段普攻时，散华自身暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"散华攻击生命低于70%的目标时，造成的伤害提升35%。"
        attr.add_dmg_bonus(0.35, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"引爆【冰棱】或【冰川】后，队伍中的角色攻击提升10%*2"
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


def calc_damage_4(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
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
    title = f"冰川爆炸伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-凝冰"
            msg = f"施放变奏技能时，散华的共鸣技能伤害提升20%"
            attr.add_dmg_bonus(0.2, title, msg)

        title = f"{role_name}-固有技能-瀑雪"
        msg = "施放第5段普攻后，冰绽造成的伤害提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一命"
        msg = f"施放第5段普攻时，散华自身暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三命"
        msg = f"散华攻击生命低于70%的目标时，造成的伤害提升35%。"
        attr.add_dmg_bonus(0.35, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五命"
        msg = "冰绽的暴击伤害提升100%。"
        attr.add_crit_dmg(1, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"引爆【冰棱】或【冰川】后，队伍中的角色攻击提升10%*2"
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

    return calc_damage_3(attr, role, isGroup)


damage_detail = [
    {
        "title": "冰棱伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "冰棱爆炸伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "冰川伤害",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "冰川爆炸伤害",
        "func": lambda attr, role: calc_damage_4(attr, role),
    },
    {
        "title": "重击·爆裂伤害",
        "func": lambda attr, role: calc_damage_0(attr, role),
    },
    {
        "title": "0+1守/0+0长离/冰川伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    }
]

rank = damage_detail[5]
