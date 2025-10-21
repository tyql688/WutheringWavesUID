# 忌炎
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    cast_hit,
    cast_liberation,
    hit_damage,
    skill_damage_calc,
)
from .buff import motefei_buff, weilinai_buff
from .damage import echo_damage, phase_damage, weapon_damage


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    破阵之枪第一段
    """
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 破阵之枪第一段 技能倍率
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    title = "破阵之枪第一段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = [cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-垂天平澜"
            msg = "施放变奏技能攻其不备后，忌炎的攻击提升10%"
            attr.add_atk_percent(0.1, title, msg)

        title = f"{role_name}-固有技能-蕴风集流"
        msg = "攻击命中目标时，忌炎的暴击伤害提升12%"
        attr.add_crit_dmg(0.12, title, msg)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()

    if chain_num >= 2 and isGroup:
        # 2命
        title = f"{role_name}-二链"
        msg = "施放变奏技能后，忌炎的攻击提升28%"
        attr.add_atk_percent(0.25, title, msg)

    if chain_num >= 3:
        # 3命
        title = f"{role_name}-三链"
        msg = "施放共鸣解放或变奏技能攻其不备时，忌炎的暴击提升16%、暴击伤害提升32%"
        attr.add_crit_rate(0.16)
        attr.add_crit_dmg(0.32)
        attr.add_effect(title, msg)

    if chain_num >= 4:
        # 4命
        title = f"{role_name}-四链"
        msg = "施放共鸣解放时，队伍中的角色重击伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 5:
        # 5命
        title = f"{role_name}-五链"
        msg = "攻击命中目标时，忌炎的攻击提升3%，可叠加15层"
        attr.add_atk_percent(0.45, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    重击·破阵之枪
    """
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 破阵之枪第一段 技能倍率
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    title = "破阵之枪第一段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "2", skillLevel)
    title = "破阵之枪第二段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "3", skillLevel)
    title = "破阵之枪第三段"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = [cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-垂天平澜"
            msg = "施放变奏技能攻其不备后，忌炎的攻击提升10%"
            attr.add_atk_percent(0.1, title, msg)

        title = f"{role_name}-固有技能-蕴风集流"
        msg = "攻击命中目标时，忌炎的暴击伤害提升12%"
        attr.add_crit_dmg(0.12, title, msg)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()

    if chain_num >= 2 and isGroup:
        # 2命
        title = f"{role_name}-二链"
        msg = "施放变奏技能后，忌炎的攻击提升28%"
        attr.add_atk_percent(0.25, title, msg)

    if chain_num >= 3:
        # 3命
        title = f"{role_name}-三链"
        msg = "施放共鸣解放或变奏技能攻其不备时，忌炎的暴击提升16%、暴击伤害提升32%"
        attr.add_crit_rate(0.16)
        attr.add_crit_dmg(0.32)
        attr.add_effect(title, msg)

    if chain_num >= 4:
        # 4命
        title = f"{role_name}-四链"
        msg = "施放共鸣解放时，队伍中的角色重击伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 5:
        # 5命
        title = f"{role_name}-五链"
        msg = "攻击命中目标时，忌炎的攻击提升3%，可叠加15层"
        attr.add_atk_percent(0.45, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_3(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> tuple[str, str]:
    """
    苍躣八荒·后动
    """
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    # 破阵之枪第一段 技能倍率
    skillLevel = role.get_skill_level("共鸣回路")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "7", "1", skillLevel)
    title = "苍躣八荒·后动"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色等级
    attr.set_character_level(role_level)

    damage_func = [cast_liberation, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    if role_breach and role_breach >= 3:
        if isGroup:
            title = f"{role_name}-固有技能-垂天平澜"
            msg = "施放变奏技能攻其不备后，忌炎的攻击提升10%"
            attr.add_atk_percent(0.1, title, msg)

        title = f"{role_name}-固有技能-蕴风集流"
        msg = "攻击命中目标时，忌炎的暴击伤害提升12%"
        attr.add_crit_dmg(0.12, title, msg)

    attr.set_phantom_dmg_bonus()

    chain_num = role.get_chain_num()

    if chain_num >= 2 and isGroup:
        # 2命
        title = f"{role_name}-二链"
        msg = "施放变奏技能后，忌炎的攻击提升28%"
        attr.add_atk_percent(0.25, title, msg)

    if chain_num >= 3:
        # 3命
        title = f"{role_name}-三链"
        msg = "施放共鸣解放或变奏技能攻其不备时，忌炎的暴击提升16%、暴击伤害提升32%"
        attr.add_crit_rate(0.16)
        attr.add_crit_dmg(0.32)
        attr.add_effect(title, msg)

    if chain_num >= 4:
        # 4命
        title = f"{role_name}-四链"
        msg = "施放共鸣解放时，队伍中的角色重击伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 5:
        # 5命
        title = f"{role_name}-五链"
        msg = "攻击命中目标时，忌炎的攻击提升3%，可叠加15层"
        attr.add_atk_percent(0.45, title, msg)

    if chain_num >= 6:
        # 6命
        title = f"{role_name}-六链"
        msg = "苍躣八荒·后动的伤害倍率提升120%*2"
        attr.add_skill_ratio(1.2 * 2, title, msg)

    # 声骸技能
    echo_damage(attr, isGroup)

    # 武器谐振
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_5(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = True
) -> tuple[str, str]:
    """
    0维/6+1莫/重击·破阵之枪
    """
    attr.set_char_damage(hit_damage)
    attr.set_char_template("temp_atk")

    # 维里奈buff
    weilinai_buff(attr, 0, 1, isGroup)

    # 莫特斐buff
    motefei_buff(attr, 6, 1, isGroup)

    return calc_damage_2(attr, role, isGroup)


damage_detail = [
    {
        "title": "破阵之枪第一段",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "重击·破阵之枪",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
    {
        "title": "苍躣八荒·后动",
        "func": lambda attr, role: calc_damage_3(attr, role),
    },
    {
        "title": "0维/6+1莫/重击·破阵之枪",
        "func": lambda attr, role: calc_damage_5(attr, role),
    },
]

rank = damage_detail[1]
