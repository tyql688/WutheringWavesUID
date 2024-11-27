from typing import Union, List

from ...api.model import WeaponData, RoleDetailData
from ...ascension.sonata import get_sonata_detail
from ...damage.abstract import WavesWeaponRegister, WavesEchoRegister
from ...damage.damage import DamageAttribute
from ...damage.utils import SONATA_CELESTIAL, SONATA_SINKING, SONATA_MOLTEN, SONATA_VOID, \
    SONATA_FREEZING, SONATA_SIERRA, SONATA_REJUVENATING, cast_hit, cast_attack, cast_skill


def weapon_damage(attr: DamageAttribute, weapon_data: WeaponData, damage_func: Union[List[str], str], isGroup: bool):
    # 武器谐振
    weapon_clz = WavesWeaponRegister.find_class(weapon_data.weapon.weaponId)
    if weapon_clz:
        w = weapon_clz(weapon_data.weapon.weaponId,
                       weapon_data.level,
                       weapon_data.breach,
                       weapon_data.resonLevel)
        w.do_action(damage_func, attr, isGroup)


def echo_damage(attr: DamageAttribute, isGroup: bool):
    # 声骸计算
    echo_clz = WavesEchoRegister.find_class(attr.echo_id)
    if echo_clz:
        e = echo_clz()
        e.do_echo(attr, isGroup)


def check_if_ph_5(ph_name: str, ph_num: int, check_name: str):
    return ph_name == check_name and ph_num == 5


def phase_damage(attr: DamageAttribute, role: RoleDetailData, damage_func: Union[List[str], str], isGroup: bool = False,
                 isHealing: bool = False):
    role_name = role.role.roleName

    if not attr.ph_detail:
        return

    for ph_detail in attr.ph_detail:
        # 凝夜白霜
        if (cast_hit in damage_func or cast_attack in damage_func) and check_if_ph_5(ph_detail.ph_name,
                                                                                     ph_detail.ph_num, SONATA_FREEZING):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

        # 熔山裂谷
        elif (cast_skill in damage_func) and check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_MOLTEN):
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

        # 彻空冥雷
        elif check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_VOID):
            if cast_skill in damage_func:
                title = f"{role_name}-{ph_detail.ph_name}"
                msg = f"使用共鸣技能时，获得一层导电伤害提升15%"
                attr.add_dmg_bonus(0.15, title, msg)
            if cast_hit in damage_func:
                title = f"{role_name}-{ph_detail.ph_name}"
                msg = f"使用重击时，获得一层导电伤害提升15%"
                attr.add_dmg_bonus(0.15, title, msg)

        # 啸谷长风
        elif isGroup and check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_SIERRA):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_atk_percent(0.3, title, msg)

        # 浮星祛暗
        elif isGroup and check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_CELESTIAL):
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

        # 沉日劫明
        elif (cast_hit in damage_func or cast_attack in damage_func) and check_if_ph_5(ph_detail.ph_name,
                                                                                       ph_detail.ph_num,
                                                                                       SONATA_SINKING):
            # 声骸五件套
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

        # 隐世回光
        elif isHealing and check_if_ph_5(ph_detail.ph_name, ph_detail.ph_num, SONATA_REJUVENATING):
            title = f"{role_name}-{ph_detail.ph_name}"
            msg = f"{get_sonata_detail(ph_detail.ph_name).set['5']['desc']}"
            attr.add_dmg_bonus(0.3, title, msg)

        # 不绝余音
