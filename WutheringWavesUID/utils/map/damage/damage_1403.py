# 秋水
from .buff import shouanren_buff, sanhua_buff
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import skill_damage_calc, SkillType, SkillTreeMap, cast_skill, cast_attack, \
    cast_liberation, attack_damage


def calc_damage_1(attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(attack_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template('temp_atk')

    title = "默认手法"
    msg = "qre潜行跳a"
    attr.add_effect(title, msg)

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "常态攻击"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(char_result.skillTrees, SkillTreeMap[skill_type], "6", skillLevel)
    title = f"空中攻击"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_attack, cast_skill, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach

    # 设置角色技能施放是不是也有加成 eg：守岸人
    title = "施放共鸣解放"
    msg = "当攻击穿过【虚实之门】时攻击提升10%"
    attr.add_atk_percent(0.1, title, msg)

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置命座
    chain_num = role.get_chain_num()
    if chain_num >= 2:
        title = f"{role_name}-二命"
        msg = f"秋水攻击被分身嘲讽的目标时，攻击提升15%。"
        attr.add_atk_percent(0.15, title, msg)

    # if chain_num >= 3:
    #     title = f"{role_name}-三命"
    #     msg = f"空中攻击穿过【雾气】时，共造成空中攻击的50%*2伤害"
    #     attr.add_skill_ratio(0.5 * 2, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五命"
        msg = f"处于迷雾潜行时，秋水的气动伤害加成提升25%"
        attr.add_dmg_bonus(0.25, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六命"
        msg = f"共鸣解放持续时，额外增加暴击8%"
        attr.add_crit_rate(0.08, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
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

    return calc_damage_1(attr, role, isGroup)


damage_detail = [
    {
        "title": "空中攻击",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "0+1守/6散/空中攻击",
        "func": lambda attr, role: calc_damage_2(attr, role),
    }
]

rank = damage_detail[1]
