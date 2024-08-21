from pathlib import Path
from typing import Dict, List, Optional

from msgspec import json as msgjson

from gsuid_core.logger import logger

MAP_PATH = Path(__file__).parent / "map"
ALIAS_LIST = Path(__file__).parent / "alias"
CHAR_ALIAS = ALIAS_LIST / "char_alias.json"

with open(CHAR_ALIAS, "r", encoding="UTF-8") as f:
    char_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

with open(MAP_PATH / "CharId2Data.json", "r", encoding="UTF-8") as f:
    char_id_data = msgjson.decode(f.read(), type=Dict[str, Dict[str, str]])


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
    for i in char_id_data:
        chars = char_id_data[i]
        if char_name == chars["name"]:
            return i
    else:
        return None
