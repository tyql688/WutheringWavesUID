from typing import Union, List

from ...api.model import WeaponData
from ...damage.abstract import WavesWeaponRegister, WavesEchoRegister
from ...damage.damage import DamageAttribute


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
