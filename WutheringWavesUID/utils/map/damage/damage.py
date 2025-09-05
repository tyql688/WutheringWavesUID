from typing import List, Union

from ...api.model import RoleDetailData, WeaponData
from ...damage.abstract import WavesEchoRegister, WavesWeaponRegister
from ...damage.damage import DamageAttribute, check_char_id
from ...damage.utils import (
    CHAR_ATTR_CELESTIAL,
    CHAR_ATTR_FREEZING,
    CHAR_ATTR_MOLTEN,
    CHAR_ATTR_SIERRA,
    CHAR_ATTR_SINKING,
    CHAR_ATTR_VOID,
    SONATA_ANCIENT,
    SONATA_CELESTIAL,
    SONATA_CLAWPRINT,
    SONATA_CROWN_OF_VALOR,
    SONATA_EMPYREAN,
    SONATA_ETERNAL,
    SONATA_FREEZING,
    SONATA_FROSTY,
    SONATA_HARMONY,
    SONATA_LINGERING,
    SONATA_MIDNIGHT,
    SONATA_MOLTEN,
    SONATA_MOONLIT,
    SONATA_PILGRIMAGE,
    SONATA_REJUVENATING,
    SONATA_SIERRA,
    SONATA_SINKING,
    SONATA_TIDEBREAKING,
    SONATA_VOID,
    SONATA_WELKIN,
    Spectro_Frazzle_Role_Ids,
    cast_attack,
    cast_hit,
    cast_liberation,
    cast_skill,
    hit_damage,
    liberation_damage,
    phantom_damage,
    skill_damage,
)


def weapon_damage(
    attr: DamageAttribute,
    weapon_data: WeaponData,
    damage_func: Union[List[str], str],
    isGroup: bool,
):
    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(weapon_data.weapon.weaponId)
    if weapon_clz:
        w = weapon_clz(
            weapon_data.weapon.weaponId,
            weapon_data.level,
            weapon_data.breach,
            weapon_data.resonLevel,
        )
        w.do_action(damage_func, attr, isGroup)


def echo_damage(attr: DamageAttribute, isGroup: bool):
    # 声骸计算
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo(attr, isGroup)


def check_if_ph_5(ph_name: str, ph_num: int, check_name: str):
    return ph_name == check_name and ph_num == 5


def check_if_ph_3(ph_name: str, ph_num: int, check_name: str):
    return ph_name == check_name and ph_num == 3


def phase_damage(
    attr: DamageAttribute,
    role: RoleDetailData,
    damage_func: Union[List[str], str],
    isGroup: bool = False,
    isHealing: bool = False,
):
    phase_name = "合鸣效果"

    # 这里的套装效果为自身触发。buff在别的地方触发。

    if not attr.ph_detail:
        return

    for ph_detail in attr.ph_detail:
        # 凝夜白霜
        if check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_FREEZING):
            if attr.char_attr != CHAR_ATTR_FREEZING:
                return
            if cast_hit in damage_func or cast_attack in damage_func:
                # 声骸五件套
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "使用普攻或重击时，冷凝伤害提升10%，该效果可叠加三层，持续15秒"
                attr.add_dmg_bonus(0.3, title, msg)

        # 熔山裂谷
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MOLTEN):
            if attr.char_attr != CHAR_ATTR_MOLTEN:
                return
            if cast_skill in damage_func:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "使用共鸣技能时，热熔伤害提升30%，持续15秒"
                attr.add_dmg_bonus(0.3, title, msg)

        # 彻空冥雷
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_VOID):
            if cast_skill in damage_func and attr.char_attr == CHAR_ATTR_VOID:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "使用共鸣技能时，获得一层导电伤害提升15%"
                attr.add_dmg_bonus(0.15, title, msg)
            if cast_hit in damage_func and attr.char_attr == CHAR_ATTR_VOID:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "使用重击时，获得一层导电伤害提升15%"
                attr.add_dmg_bonus(0.15, title, msg)

        # 啸谷长风
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SIERRA):
            if not isGroup:
                return
            if attr.char_attr != CHAR_ATTR_SIERRA:
                return
            # 声骸五件套
            title = f"{phase_name}-{ph_detail.ph_name}"
            msg = "使用变奏技能登场时，气动伤害提升30%，持续15秒"
            attr.add_atk_percent(0.3, title, msg)

        # 浮星祛暗
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_CELESTIAL):
            if not isGroup:
                return
            if attr.char_attr != CHAR_ATTR_CELESTIAL:
                return
            title = f"{phase_name}-{ph_detail.ph_name}"
            msg = "使用变奏技能登场时，衍射伤害提升30%，持续15秒"
            attr.add_dmg_bonus(0.3, title, msg)

        # 沉日劫明
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SINKING):
            if attr.char_attr != CHAR_ATTR_SINKING:
                return
            if cast_hit in damage_func or cast_attack in damage_func:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "使用普攻或重击时，湮灭伤害提升7.5%，该效果可叠加四层，持续15秒"
                attr.add_dmg_bonus(0.3, title, msg)

        # 隐世回光
        elif isHealing and check_if_ph_5(
            ph_detail.ph_name, ph_detail.ph_num, SONATA_REJUVENATING
        ):
            if attr.char_template != "temp_atk":
                return
            title = f"{phase_name}-{ph_detail.ph_name}"
            msg = "自身为友方提供治疗时，全队共鸣者攻击提升15%，持续30秒"
            attr.add_atk_percent(0.15, title, msg)

        # 轻云出月
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MOONLIT):
            pass
        # 不绝余音 查无此人
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_LINGERING):
            pass
        # 凌冽决断之心 -新冷凝
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_FROSTY):
            if cast_skill in damage_func and attr.char_attr == CHAR_ATTR_FREEZING:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "施放共鸣技能时，自身冷凝伤害提升22.5%"
                attr.add_dmg_bonus(0.225, title, msg)
            if cast_liberation in damage_func and attr.char_damage == skill_damage:
                title = f"{phase_name}-{ph_detail.ph_name}"
                if check_char_id(attr, [1107]):
                    msg = "施放共鸣解放时，自身共鸣技能伤害提升18%*2"
                    attr.add_dmg_bonus(0.18 * 2, title, msg)
                else:
                    title = f"{phase_name}-{ph_detail.ph_name}"
                    msg = "施放共鸣解放时，自身共鸣技能伤害提升18%"
                    attr.add_dmg_bonus(0.18, title, msg)

        # 高天共奏之曲 -协同
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_EMPYREAN):
            if attr.sync_strike:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "当前角色协同攻击造成的伤害提升80%"
                attr.add_dmg_bonus(0.8, title, msg)

                # 协同攻击命中敌人且暴击时，队伍中登场角色攻击力提升20%
                if attr.char_template == "temp_atk":
                    title = f"{phase_name}-{ph_detail.ph_name}"
                    msg = "协同攻击命中敌人且暴击时，队伍中登场角色攻击力提升20%"
                    attr.add_atk_percent(0.2, title, msg)

        # 幽夜隐匿之帷
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MIDNIGHT):
            # 角色触发延奏技能离场时，额外对周围敌人造成480%的湮灭伤害，该伤害为延奏技能伤害，并使下一个登场角色湮灭属性伤害加成提升15%，持续15秒
            pass

        # 此间永驻之光
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_ETERNAL):
            if not check_char_id(attr, Spectro_Frazzle_Role_Ids):
                return
            # 角色为敌人添加【光噪效应】时，自身暴击提升20%，持续15秒；攻击存在10层【光噪效应】的敌人时，自身衍射伤害加成提升15%，持续15秒。
            title = f"{phase_name}-{ph_detail.ph_name}"
            msg = "角色为敌人添加【光噪效应】时，自身暴击提升20%"
            attr.add_crit_rate(0.2, title, msg)
            if attr.char_attr == CHAR_ATTR_CELESTIAL:
                msg = "攻击存在10层【光噪效应】的敌人时，自身衍射伤害加成提升15%"
                attr.add_dmg_bonus(0.15, title, msg)

        # 无惧浪涛之勇
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_TIDEBREAKING):
            # 角色攻击提升15%，共鸣效率达到250%后，当前角色全属性伤害提升30%
            title = f"{phase_name}-{ph_detail.ph_name}"
            if attr.char_template == "temp_atk":
                msg = "角色攻击提升15%"
                if attr.ph_result:
                    attr.add_effect(title, msg)
                else:
                    attr.add_dmg_bonus(0.15, title, msg)

            if attr.energy_regen >= 2.5:
                msg = "共鸣效率达到250%后，当前角色全属性伤害提升30%"
                if attr.ph_result:
                    attr.add_effect(title, msg)
                else:
                    attr.add_dmg_bonus(0.3, title, msg)

        # 流云逝尽之空
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_WELKIN):
            # 角色为敌人添加【风蚀效应】时，队伍中角色气动伤害提升15%，自身气动伤害额外提升15%，持续20秒。
            if attr.char_attr != CHAR_ATTR_SIERRA:
                return
            if attr.env_aero_erosion:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "角色为敌人添加【风蚀效应】时，队伍中角色气动伤害提升15%"
                attr.add_dmg_bonus(0.15, title, msg)

                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "自身气动伤害额外提升15%"
                attr.add_dmg_bonus(0.15, title, msg)

        # 愿戴荣光之旅
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_PILGRIMAGE):
            # 攻击命中存在【风蚀效应】的敌人时，自身暴击提升10%，气动伤害提升30%，持续10秒。
            if attr.env_aero_erosion:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "攻击命中存在【风蚀效应】的敌人时，自身暴击提升10%"
                attr.add_crit_rate(0.1, title, msg)
                if attr.char_attr == CHAR_ATTR_SIERRA:
                    msg = "气动伤害提升30%"
                    attr.add_dmg_bonus(0.3, title, msg)

        # 奔狼燎原之焰
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_CLAWPRINT):
            # 施放共鸣解放时，队伍中角色热熔伤害提升15%，自身共鸣解放伤害提升20%，持续35秒。
            if attr.char_attr == CHAR_ATTR_MOLTEN:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "施放共鸣解放时，队伍中角色热熔伤害提升15%"
                attr.add_dmg_bonus(0.15, title, msg)

            if attr.char_damage == liberation_damage:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "自身共鸣解放伤害提升20%"
                attr.add_dmg_bonus(0.2, title, msg)
        # 失序彼岸之梦
        elif check_if_ph_3(ph_detail.ph_name, ph_detail.ph_num, SONATA_ANCIENT):
            # 角色共鸣能量为0时，自身暴击率提升20%，声骸技能伤害加成提升35%
            title = f"{phase_name}-{ph_detail.ph_name}"
            if attr.char_template == "temp_atk":
                msg = "角色共鸣能量为0时，自身暴击率提升20%"
                if attr.ph_result:
                    attr.add_effect(title, msg)
                else:
                    attr.add_crit_rate(0.2, title, msg)

            if attr.char_damage == phantom_damage:
                msg = "角色共鸣能量为0时，声骸技能伤害加成提升35%"
                if attr.ph_result:
                    attr.add_effect(title, msg)
                else:
                    attr.add_dmg_bonus(0.35, title, msg)

        # 荣斗铸锋之冠
        elif check_if_ph_3(ph_detail.ph_name, ph_detail.ph_num, SONATA_CROWN_OF_VALOR):
            # 角色获得护盾时，自身攻击提升6%，暴击伤害提升4%，该效果可叠加5层，持续4秒，每0.5秒可触发一次。
            if not attr.trigger_shield:
                return
            title = f"{phase_name}-{ph_detail.ph_name}"
            msg = "角色获得护盾时，自身攻击提升6%*5"
            attr.add_atk_percent(0.06 * 5, title, msg)
            msg = "角色获得护盾时，自身暴击伤害提升4%*5"
            attr.add_crit_dmg(0.04 * 5, title, msg)

        # 息界同调之律
        elif check_if_ph_3(ph_detail.ph_name, ph_detail.ph_num, SONATA_HARMONY):
            # 角色施放声骸技能时，自身重击伤害加成提升30%，持续4秒；队伍中角色声骸技能伤害加成提升4%，该效果可叠加4层，持续30秒。
            # ？
            if attr.char_damage == hit_damage:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "角色施放声骸技能时，自身重击伤害加成提升30%"
                attr.add_dmg_bonus(0.3, title, msg)
            if attr.char_damage == phantom_damage:
                title = f"{phase_name}-{ph_detail.ph_name}"
                msg = "队伍中角色声骸技能伤害加成提升4%*4"
                attr.add_dmg_bonus(0.04 * 4, title, msg)
