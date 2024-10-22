import copy
from pathlib import Path
from typing import Union

from msgspec import json as msgjson

from gsuid_core.logger import logger

MAP_PATH = Path(__file__).parent / "map/detail_json/char"
char_id_data = {}


def read_char_json_files(directory):
    files = directory.rglob('*.json')

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = msgjson.decode(f.read())
                file_name = file.name.split('.')[0]
                char_id_data[file_name] = data
        except Exception as e:
            logger.exception(f"read_char_json_files load fail decoding {file}", e)


read_char_json_files(MAP_PATH)


class WavesCharResult:
    def __int__(self):
        self.name = None
        self.starLevel = None
        self.stats = None


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


def get_char_detail(
    char_id: Union[str, int],
    level: int,
    breach: Union[int, None] = None
) -> Union[WavesCharResult, None]:
    """
    breach 突破
    resonLevel 精炼
    """
    if str(char_id) not in char_id_data:
        logger.exception(f"get_char_detail char_id: {char_id} not found")
        return None

    breach = get_breach(breach, level)

    char_data = char_id_data[str(char_id)]
    result = WavesCharResult()
    result.name = char_data["name"]
    result.starLevel = char_data["starLevel"]
    result.stats = copy.deepcopy(char_data["stats"][str(breach)][str(level)])

    return result
