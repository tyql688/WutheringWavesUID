import json
from pathlib import Path
from ..utils.resource.constant import SONATA_FIRST_ID

PLUGIN_PATH =  Path(__file__).parent.parent
FETTERDETAIL_PATH = PLUGIN_PATH / "utils/map/detail_json/sonata"


DETAIL = {
    "今汐": {
        "id": "1304",
        "fetterDetail": "浮星祛暗"
    },
    "漂泊者·湮灭": {
        "id": "1604",
        "fetterDetail": "沉日劫明"
    },
    "渊武": {
        "id": "1303",
        "fetterDetail": "高天共奏之曲"
    },
    "折枝": {
        "id": "1105",
        "fetterDetail": "高天共奏之曲"
    },
    "守岸人": {
        "id": "1505",
        "fetterDetail": "隐世回光"
    },
    "漂泊者·湮灭": {
        "id": "1605",
        "fetterDetail": "沉日劫明"
    },
    "长离": {
        "id": "1205",
        "fetterDetail": "熔山裂谷"
    },
    "菲比": {
        "id": "1506",
        "fetterDetail": "此间永驻之光"
    },
    "凌阳": {
        "id": "1104",
        "fetterDetail": "凝夜白霜"
    },
    "安可": {
        "id": "1203",
        "fetterDetail": "熔山裂谷"
    },
    "吟霖": {
        "id": "1302",
        "fetterDetail": "高天共奏之曲"
    },
    "漂泊者·衍射": {
        "id": "1502",
        "fetterDetail": "此间永驻之光"
    },
    "鉴心": {
        "id": "1405",
        "fetterDetail": "啸谷长风"
    },
    "白芷": {
        "id": "1103",
        "fetterDetail": "隐世回光"
    },
    "釉瑚": {
        "id": "1106",
        "fetterDetail": "隐世回光"
    },
    "炽霞": {
        "id": "1202",
        "fetterDetail": "熔山裂谷"
    },
    "维里奈": {
        "id": "1503",
        "fetterDetail": "隐世回光"
    },
    "洛可可": {
        "id": "1606",
        "fetterDetail": "幽夜隐匿之帷"
    },
    "散华": {
        "id": "1102",
        "fetterDetail": "轻云出月"
    },
    "卡卡罗": {
        "id": "1301",
        "fetterDetail": "彻空冥雷"
    },
    "秋水": {
        "id": "1403",
        "fetterDetail": "啸谷长风"
    },
    "桃祈": {
        "id": "1601",
        "fetterDetail": "轻云出月"
    },
    "丹瑾": {
        "id": "1602",
        "fetterDetail": "沉日劫明"
    },
    "相里要": {
        "id": "1305",
        "fetterDetail": "彻空冥雷"
    },
    "布兰特": {
        "id": "1206",
        "fetterDetail": "无惧浪涛之勇"
    },
    "莫特斐": {
        "id": "1204",
        "fetterDetail": "高天共奏之曲"
    },
    "珂莱塔": {
        "id": "1107",
        "fetterDetail": "凌冽决断之心"
    },
    "灯灯": {
        "id": "1504",
        "fetterDetail": "彻空冥雷"
    },
    "椿": {
        "id": "1603",
        "fetterDetail": "沉日劫明"
    },
    "漂泊者·衍射": {
        "id": "1501",
        "fetterDetail": "此间永驻之光"
    },
    "忌炎": {
        "id": "1404",
        "fetterDetail": "啸谷长风"
    },
    "秧秧": {
        "id": "1402",
        "fetterDetail": "彻空冥雷"
    }
}

async def get_fetterDetail_from_sonata(char_name) -> tuple[str, dict]:
    
    path = FETTERDETAIL_PATH / f"{DETAIL[char_name]['fetterDetail']}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    first_echo_id = SONATA_FIRST_ID[data["name"]][0]

    echo = {
        "cost": 1,
        "level": 25,
        "quality": 5,
        "fetterDetail": {
            "firstDescription": data["set"]["2"]["desc"],
            "groupId": 0,
            "iconUrl": "",
            "name": data["name"],
            "num": 5,
            "secondDescription": data["set"]["5"]["desc"]
        },
        "phantomProp": {
            "cost": 1,
            "iconUrl": "",
            "name": data["name"],
            "phantomId": 391070105,
            "phantomPropId": 0,
            "quality": 5,
            "skillDescription": "龟"
        }
    }
    return first_echo_id, echo
