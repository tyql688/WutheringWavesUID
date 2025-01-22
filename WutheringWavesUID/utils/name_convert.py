from pathlib import Path
from typing import Dict, List, Optional

from msgspec import json as msgjson

from gsuid_core.logger import logger

MAP_PATH = Path(__file__).parent / "map"
ALIAS_LIST = Path(__file__).parent / "alias"
CHAR_ALIAS = ALIAS_LIST / "char_alias.json"
WEAPON_ALIAS = ALIAS_LIST / "weapon_alias.json"

with open(CHAR_ALIAS, "r", encoding="UTF-8") as f:
    char_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

with open(WEAPON_ALIAS, "r", encoding="UTF-8") as f:
    weapon_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

with open(MAP_PATH / "CharId2Data.json", "r", encoding="UTF-8") as f:
    char_id_data = msgjson.decode(f.read(), type=Dict[str, Dict[str, str]])

with open(MAP_PATH / "id2name.json", "r", encoding="UTF-8") as f:
    id2name = msgjson.decode(f.read(), type=Dict[str, str])


def alias_to_char_name(char_name: str) -> str:
    for i in char_alias_data:
        if (char_name in i) or (char_name in char_alias_data[i]):
            logger.debug(f"别名转换: {char_name} -> {i}")
            return i
    return char_name


def char_id_to_char_name(char_id: str) -> Optional[str]:
    char_id = str(char_id)
    if char_id in char_id_data:
        return char_id_data[char_id]["name"]
    else:
        return None


def char_name_to_char_id(char_name: str) -> Optional[str]:
    char_name = alias_to_char_name(char_name)
    for id, name in id2name.items():
        if char_name == name:
            return id
    else:
        return None


def alias_to_weapon_name(weapon_name: str) -> str:
    for i in weapon_alias_data:
        if (weapon_name in i) or (weapon_name in weapon_alias_data[i]):
            return i
    return weapon_name


def weapon_name_to_weapon_id(weapon_name: str) -> Optional[str]:
    weapon_name = alias_to_weapon_name(weapon_name)
    for id, name in id2name.items():
        if weapon_name == name:
            return id
    else:
        return None


def get_all_char_id() -> List[str]:
    return list(char_id_data.keys())
