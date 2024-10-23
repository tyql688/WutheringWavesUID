from pathlib import Path
from typing import Union

from msgspec import json as msgjson

from gsuid_core.logger import logger

MAP_PATH = Path(__file__).parent / "map/detail_json/sonata"
sonata_id_data = {}


def read_sonata_json_files(directory):
    files = directory.rglob('*.json')

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = msgjson.decode(f.read())
                file_name = file.name.split('.')[0]
                sonata_id_data[file_name] = data
        except Exception as e:
            logger.exception(f"read_char_json_files load fail decoding {file}", e)


read_sonata_json_files(MAP_PATH)


class WavesSonataResult:
    def __int__(self):
        self.name = None
        self.set = None


def get_sonata_detail(
    sonata_name: str
) -> Union[WavesSonataResult, None]:
    if str(sonata_name) not in sonata_id_data:
        logger.exception(f"get_sonata_detail sonata_name: {sonata_name} not found")
        return None

    char_data = sonata_id_data[sonata_name]
    result = WavesSonataResult()
    result.name = char_data["name"]
    result.set = char_data["set"]
    return result
