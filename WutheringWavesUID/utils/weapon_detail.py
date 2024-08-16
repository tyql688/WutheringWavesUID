import copy
from typing import Union

from msgspec import json as msgjson

from ..utils.name_convert import MAP_PATH

with open(MAP_PATH / "weaponData.json", "r", encoding="UTF-8") as f:
    weapon_id_data = msgjson.decode(f.read())


class WavesWeaponResult:
    def __int__(self):
        self.name = None
        self.starLevel = None
        self.type = None
        self.stats = None
        self.effect = None
        self.effectName = None


def get_breach(breach: Union[int, None], level: int):
    if breach is None:
        if level <= 20:
            breach = 0
        elif level <= 40:
            breach = 1
        elif level <= 50:
            breach = 2
        elif level <= 60:
            breach = 3
        elif level <= 70:
            breach = 4
        elif level <= 80:
            breach = 5
        elif level <= 90:
            breach = 6
    return breach


def get_weapon_detail(
    weapon_id: Union[str, int],
    level: int,
    breach: int = 0,
    resonLevel: Union[int, None] = 1
) -> WavesWeaponResult | None:
    """
    breach 突破
    resonLevel 精炼
    """
    if str(weapon_id) not in weapon_id_data:
        return None

    breach = get_breach(breach, level)

    weapon_data = weapon_id_data[str(weapon_id)]
    result = WavesWeaponResult()
    result.name = weapon_data["name"]
    result.starLevel = weapon_data["starLevel"]
    result.type = weapon_data["type"]
    result.effectName = weapon_data["effectName"]
    result.stats = copy.deepcopy(weapon_data["stats"][str(breach)][str(level)])
    effect = weapon_data["effect"]
    if resonLevel is None:
        resonLevel = 1
    for i, p in enumerate(weapon_data["param"]):
        _temp = '{' + str(i) + '}'
        effect = effect.replace(f"{_temp}", str(p[resonLevel - 1]))
    result.effect = effect

    for stat in result.stats:
        if stat["isPercent"]:
            stat["value"] = f'{stat["value"] / 100:.1f}%'
        elif stat["isRatio"]:
            stat["value"] = f'{stat["value"] * 100:.1f}%'
        else:
            stat["value"] = f'{int(stat["value"])}'

    return result
