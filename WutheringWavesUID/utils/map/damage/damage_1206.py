# 船长
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    SkillTreeMap,
    SkillType,
    attack_damage,
    cast_attack,
    cast_liberation,
    cast_skill,
    liberation_damage,
    skill_damage_calc,
)
from .buff import sanhua_buff, shouanren_buff, lupa_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute,
    role: RoleDetailData,
    isGroup: bool = False,
    is_single: bool = False,
) -> tuple[str, str]:
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
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
    if is_single:
        skill_multi = skill_multi.split("+")[-1]
    title = "火焰归亡曲"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-迎海投火的决意"
        msg = "热熔伤害加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人
    if attr.energy_regen > 1.5:
        title = f"{role_name}-「我」的人生"
        atk_flat = int((attr.energy_regen - 1.5) * 2000)
        if atk_flat > 2600:
            atk_flat = 2600
        msg = f"每超1%为20点攻击提升，上限为2600，当前提升{atk_flat}"
        attr.add_atk_flat(atk_flat, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "每次空中攻击空翻时，布兰特造成伤害提升20%，可叠加3层。"
        attr.add_dmg_bonus(0.2 * 3, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = "施放空中攻击和火焰归亡曲时暴击提升30%"
        attr.add_crit_rate(0.3, title, msg)

    if chain_num >= 3:
        title = f"{role_name}-三链"
        msg = "火焰归亡曲伤害倍率提升42%。"
        attr.add_skill_ratio(0.42, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = "造成普攻伤害时，普攻伤害加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

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
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

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
    title = "直到世界尽头"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-迎海投火的决意"
        msg = "热熔伤害加成提升15%"
        attr.add_dmg_bonus(0.15, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人
    if attr.energy_regen > 1.5:
        title = f"{role_name}-戏中人生"
        atk_flat = int((attr.energy_regen - 1.5) * 1200)
        if atk_flat > 1560:
            atk_flat = 1560
        msg = f"每超1%为12点攻击提升，上限为1560，当前提升{atk_flat}"
        attr.add_atk_flat(atk_flat, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = "每次空中攻击空翻时，布兰特造成伤害提升20%，可叠加3层。"
        attr.add_dmg_bonus(0.2 * 3, title, msg)

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
    attr.set_char_damage(attack_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 散华buff
    sanhua_buff(attr, 6, 1, isGroup)

    return calc_damage_1(attr, role, isGroup)


def calc_damage_11(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(attack_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 露帕buff
    lupa_buff(attr, 0, 1, isGroup)

    # 露帕解放火队人数buff
    title = "露帕-追猎-共鸣解放"
    msg = "热熔提升10%"
    attr.add_dmg_bonus(0.1, title, msg)

    return calc_damage_1(attr, role, isGroup)
    

def calc_damage_12(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    attr.set_char_damage(attack_damage)
    attr.set_char_template("temp_atk")
    # 守岸人buff
    shouanren_buff(attr, 0, 1, isGroup)

    # 露帕buff
    lupa_buff(attr, 6, 5, isGroup)

    # 露帕解放火队人数buff
    title = "露帕-追猎-共鸣解放"
    msg = "热熔提升(10+10)%"
    attr.add_dmg_bonus(0.2, title, msg)

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "火焰归亡曲尾刀",
        "func": lambda attr, role: calc_damage_1(attr, role, is_single=True),
    },
    {
        "title": "火焰归亡曲伤害",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "直到世界尽头伤害",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "0+1守/6散/火焰归亡曲伤害",
        "func": lambda attr, role: calc_damage_10(attr, role),
    },
    {
        "title": "0+1守/0+1露/火焰归亡曲伤害",
        "func": lambda attr, role: calc_damage_11(attr, role),
    },
    {
        "title": "0+1守/6+5露/火焰归亡曲伤害",
        "func": lambda attr, role: calc_damage_12(attr, role),
    },
]

rank = damage_detail[0]
