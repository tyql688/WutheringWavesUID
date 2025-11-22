# 卜灵

from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    cast_attack,
    cast_liberation,
    cast_skill,
    heal_bonus,
    hit_damage,
    skill_damage_calc,
)
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    召劾鬼神治疗量
    """
    attr.set_char_damage(heal_bonus)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "变奏技能"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 治疗倍率 召劾鬼神 145.13% + 1270
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "32", skillLevel
    )
    title = "召劾鬼神治疗量"
    msg = f"技能倍率{skill_multi}"
    attr.add_healing_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置角色固有技能
    if role_breach is not None and role_breach >= 3:
        title = "固有技能-吉时已至"
        msg = "治疗生命值低于50%的角色时，治疗效果加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus(needShuxing=False)

    # 设置共鸣链
    chain_num = role.get_chain_num()
    # 二链：回复共鸣能量，不影响治疗量

    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "卜灵的治疗效果加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 治疗量
    healing_bonus = attr.calculate_healing(attr.effect_attack)
    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    三链-五雷荡煞阵触发治疗
    """
    attr.set_char_damage(heal_bonus)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach

    # 检查是否有三链
    chain_num = role.get_chain_num()
    if chain_num < 3:
        return None, "0"

    # 三链
    title = "三链-五雷荡煞阵触发治疗"
    msg = "技能倍率350+150.00%"
    attr.add_healing_skill_multi("350+150.00%", title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill]

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置角色固有技能
    if role_breach is not None and role_breach >= 3:
        title = "固有技能-吉时已至"
        msg = "治疗生命值低于50%的角色时，治疗效果加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus(needShuxing=False)

    # 设置共鸣链
    if chain_num >= 4:
        title = f"{role_name}-四链"
        msg = "卜灵的治疗效果加成提升20%"
        attr.add_dmg_bonus(0.2, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 治疗量
    healing_bonus = attr.calculate_healing(attr.effect_attack)
    crit_damage = f"{healing_bonus:,.0f}"
    return None, crit_damage


def calc_damage_3(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    飞雷诀·归一伤害
    """
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能倍率 飞雷诀·归一 979.59%
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "25", skillLevel
    )
    title = "飞雷诀·归一伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role_level)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "共鸣解放·飞雷诀·归一造成伤害时，暴击提升20%"
        attr.add_crit_rate(0.2, title, msg)

    # 四链：治疗效果加成提升，不影响伤害
    # 六链：队伍中登场角色获得的共鸣技能伤害加成效果提升至50%（这是buff效果，不直接影响飞雷诀伤害计算）

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "召劾鬼神治疗量",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "三链-五雷荡煞阵触发治疗",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "飞雷诀·归一伤害",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
]

rank = damage_detail[0]
