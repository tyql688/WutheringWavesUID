# 菲比
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_skill,
    hit_damage,
    liberation_damage,
    skill_damage_calc,
)
from .buff import guangzhu_buff, shouanren_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    use_type="赦罪",
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    attr.add_effect("默认手法", "zeqr")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = "启明之誓愿"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_attack, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-启示"
        msg = "处于赦罪or告解时，衍射伤害加成提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if use_type == "赦罪":
        if chain_num >= 1:
            title = f"{role_name}-一链"
            msg = "赦罪状态: 伤害倍率提升255%->480%"
            attr.add_skill_ratio(4.8, title, msg)
        else:
            title = "赦罪状态"
            msg = "赦罪状态: 伤害倍率提升255%"
            attr.add_skill_ratio(2.55, title, msg)
    else:
        if chain_num >= 1:
            title = f"{role_name}-一链"
            msg = "告解状态: 伤害倍率提升90%"
            attr.add_skill_ratio(0.9, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "目标衍射伤害抗性降低10%"
        attr.add_enemy_resistance(-0.1, title, msg)

    if chain_num >= 5 and isGroup:
        title = f"{role_name}-五链"
        msg = "变奏入场，菲比的衍射伤害加成提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "赦罪or告解状态,菲比施放共鸣技能召唤【镜之环】时,攻击提升10%"
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


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = "圣祷赦罪"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_attack, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-启示"
        msg = "处于赦罪or告解时，衍射伤害加成提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "目标衍射伤害抗性降低10%"
        attr.add_enemy_resistance(-0.1, title, msg)

    if chain_num >= 5 and isGroup:
        title = f"{role_name}-五链"
        msg = "变奏入场，菲比的衍射伤害加成提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_3(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    use_type: str = "赦罪",
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(hit_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")
    # 设置光噪效应
    attr.set_env_spectro()

    attr.add_effect("默认手法", "zqaaaz")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )
    title = "重击·星辉"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_attack, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-启示"
        msg = "处于赦罪or告解时，衍射伤害加成提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人
    if use_type == "赦罪":
        title = f"{role_name}-赦罪状态"
        msg = "赦罪状态：命中的目标拥有【光噪效应】时，伤害加深256%"
        attr.add_dmg_deepen(2.56, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()

    if chain_num >= 3:
        if use_type == "赦罪":
            title = f"{role_name}-三链"
            msg = "赦罪状态: 重击星辉伤害倍率提升91%"
            attr.add_skill_ratio(0.91, title, msg)
        else:
            title = f"{role_name}-三链"
            msg = "告解状态：重击星辉伤害倍率提升249%"
            attr.add_skill_ratio(2.49, title, msg)

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "目标衍射伤害抗性降低10%"
        attr.add_enemy_resistance(-0.1, title, msg)

    if chain_num >= 5 and isGroup:
        title = f"{role_name}-五链"
        msg = "变奏入场，菲比的衍射伤害加成提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = "赦罪or告解状态,菲比施放共鸣技能召唤【镜之环】时,攻击提升10%"
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


def calc_damage_10(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 光主buff
    guangzhu_buff(attr, 6, 1, isGroup)

    return calc_damage_3(attr, role, isGroup)


damage_detail = [
    {
        "title": "赦罪-重击·星辉伤害",
        "func": lambda attr, role: calc_damage_3(attr, role, use_type="赦罪"),
    },
    {
        "title": "赦罪-启明之誓愿伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, use_type="赦罪"),
    },
    {
        "title": "告解-重击·星辉伤害",
        "func": lambda attr, role: calc_damage_3(attr, role, use_type="告解"),
    },
    {
        "title": "告解-启明之誓愿伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, use_type="告解"),
    },
    {
        "title": "圣祷赦罪伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "0+1守/6光/赦罪-z伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    },
]

rank = damage_detail[0]
