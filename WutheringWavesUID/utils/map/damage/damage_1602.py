# 丹瑾
from typing import Union, List

from .damage import weapon_damage, echo_damage
from ...api.model import RoleDetailData
from ...ascension.char import get_char_detail, WavesCharResult
from ...ascension.sonata import get_sonata_detail
from ...damage.damage import DamageAttribute
from ...damage.utils import check_if_ph_5, SONATA_SINKING, skill_damage_calc, hit_damage, cast_skill, cast_hit, \
    liberation_damage, cast_liberation


def calc_damage(attr: DamageAttribute, role: RoleDetailData, damage_func, isGroup: bool = False):
    role_name = role.role.roleName
    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach

    # 设置角色等级
    attr.set_character_level(role_level)

    for ph_detail in attr.ph_detail:
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SINKING):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

    chain_num = role.get_chain_num()
    if role_breach >= 3:
        # 固有技能
        title = f"{role_name}-固有技能-盈溢"
        msg = "施放共鸣技能后，重击伤害提升30%。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 1:
        # 1命
        title = f"{role_name}-一命"
        msg = f"自身的攻击提升5%*6"
        attr.add_atk_percent(0.3, title, msg)

    if chain_num >= 2:
        # 2命
        title = f"{role_name}-二命"
        msg = "丹瑾攻击携带朱蚀之刻的目标时，造成的伤害额外提升20%。"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 3 and cast_liberation in damage_func:
        # 3命
        title = f"{role_name}-三命"
        msg = f"共鸣解放伤害加成提升30%。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 4:
        # 4命
        title = f"{role_name}-四命"
        msg = "【彤华】积攒60点以上时，丹瑾的暴击提升15%。"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 5:
        # 5命
        title = f"{role_name}-五命"
        msg = f"湮灭伤害加成提升15%，生命低于60%时湮灭伤害加成提升15%。"
        attr.add_dmg_bonus(0.3, title, msg)

    if chain_num >= 6:
        # 6命
        title = f"{role_name}-六命"
        msg = "施放重击缭乱时，队伍中的角色的攻击提升20%。"
        attr.add_atk_percent(0.2, title, msg)

    echo_damage(attr, isGroup)

    weapon_damage(attr, role.weaponData, damage_func, isGroup)


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False,
                  skill_type: Union[str, List[str]] = "满能缭乱") -> (
    str, str):
    """
    满能缭乱伤害
    """
    damage_func = [cast_skill, cast_hit]
    attr.set_char_damage(hit_damage)

    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    title = "默认叠buff手法"
    msg = "q闪,eaee,eaaee,eaaee,z"
    attr.add_effect(title, msg)

    title = "生命"
    msg = "低于60%"
    attr.add_effect(title, msg)

    # 绯红绽放 技能倍率 = 满能缭乱+满能纷落
    skillLevel = role.get_skill_level("共鸣回路")
    # 技能倍率
    if "满能缭乱" in skill_type:
        skill_multi = skill_damage_calc(char_result.skillTrees, "7", "3", skillLevel)
        title = "满能缭乱伤害"
        msg = f"技能倍率{skill_multi}"
        attr.add_skill_multi(skill_multi, title, msg)

    if "满能纷落" in skill_type:
        skill_multi = skill_damage_calc(char_result.skillTrees, "7", "4", skillLevel)
        title = "满能纷落伤害"
        msg = f"技能倍率{skill_multi}"
        attr.add_skill_multi(skill_multi, title, msg)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.hit_damage:
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.hit_damage)

    calc_damage(attr, role, damage_func, isGroup)
    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_4(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    """
    绯红绽放
    """
    damage_func = [cast_liberation, cast_skill]
    attr.set_char_damage(liberation_damage)

    role_id = role.role.roleId
    role_level = role.role.level
    role_breach = role.role.breach
    char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)

    title = "默认叠buff手法"
    msg = "q闪,eaee,eaaee,zr"
    attr.add_effect(title, msg)

    title = "生命"
    msg = "低于60%"
    attr.add_effect(title, msg)

    # 绯红绽放 技能倍率 = 连续攻击+绯刹爆发
    skillLevel = role.get_skill_level("共鸣解放")
    # 技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "1", skillLevel)
    title = "连续攻击"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(char_result.skillTrees, "3", "2", skillLevel)
    title = "绯刹爆发"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    if attr.dmg_bonus_phantom and attr.dmg_bonus_phantom.liberation_damage:
        attr.add_dmg_bonus(attr.dmg_bonus_phantom.liberation_damage)

    calc_damage(attr, role, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "满能缭乱伤害",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_type="满能缭乱"),
    },
    {
        "title": "丹心昭瑾",
        "func": lambda attr, role: calc_damage_1(attr, role, skill_type=["满能缭乱", "满能纷落"]),
    },
    {
        "title": "绯红绽放",
        "func": lambda attr, role: calc_damage_4(attr, role),
    },
]
