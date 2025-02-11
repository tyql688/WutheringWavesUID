import json
from pathlib import Path
from typing import List

from loguru import logger
from msgspec import json as msgjson

MAP_PATH = Path(__file__).parents[1] / "map/character"

# 声骸副词条
phantom_sub_value = [
    {"name": "攻击", "values": ["30", "40", "50", "60"]},
    {
        "name": "攻击%",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "生命",
        "values": ["320", "360", "390", "430", "470", "510", "540", "580"],
    },
    {
        "name": "生命%",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {"name": "防御", "values": ["40", "50", "60", "70"]},
    {
        "name": "防御%",
        "values": ["8.1%", "9%", "10%", "10.9%", "11.8%", "12.8%", "13.8%", "14.7%"],
    },
    {
        "name": "暴击",
        "values": ["6.3%", "6.9%", "7.5%", "8.1%", "8.7%", "9.3%", "9.9%", "10.5%"],
    },
    {
        "name": "暴击伤害",
        "values": [
            "12.6%",
            "13.8%",
            "15%",
            "16.2%",
            "17.4%",
            "18.6%",
            "19.8%",
            "21.0%",
        ],
    },
    {
        "name": "普攻伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "重击伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "共鸣技能伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "共鸣解放伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "技能伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "共鸣效率",
        "values": ["6.8%", "7.6%", "8.4%", "9.2%", "10%", "10.8%", "11.6%", "12.4%"],
    },
]
phantom_sub_value_map = {i["name"]: i["values"] for i in phantom_sub_value}

# 1, 3, 4
phantom_main_value = [
    {"name": "攻击", "values": ["0", "100", "150"]},
    {"name": "攻击%", "values": ["18%", "30%", "33%"]},
    {"name": "生命", "values": ["2280", "0", "0"]},
    {"name": "生命%", "values": ["22.8%", "30%", "33%"]},
    {"name": "防御%", "values": ["18%", "38%", "41.8%"]},
    {"name": "暴击", "values": ["0%", "0%", "22%"]},
    {"name": "暴击伤害", "values": ["0%", "0%", "44%"]},
    {"name": "共鸣效率", "values": ["0%", "32%", "0%"]},
    {"name": "属性伤害加成", "values": ["0%", "30%", "0%"]},
    {"name": "治疗效果加成", "values": ["0%", "0%", "26.4%"]},
]
phantom_main_value_map = {i["name"]: i["values"] for i in phantom_main_value}


def calc_sub_max_score(
    _temp, sub_props, jineng: float = None, skill_weight: List = None
):
    score = 0
    jineng_list = [
        "普攻伤害加成",
        "重击伤害加成",
        "共鸣技能伤害加成",
        "共鸣解放伤害加成",
    ]
    for i in _temp:
        ratio = 1
        if jineng is not None and i == "技能伤害加成":
            ratio = jineng
        elif i in jineng_list:
            ratio = skill_weight[jineng_list.index(i)]
        _phantom_value = phantom_sub_value_map[i][-1]
        if "%" in _phantom_value:
            _phantom_value = _phantom_value.replace("%", "")
        _phantom_value = float(_phantom_value)
        score += sub_props[i] * _phantom_value * ratio

    return round(score, 2)


def calc_main_max_score(_temp, main_props):
    score = []
    for k, v in _temp.items():
        cost = int(k.split(".")[0])
        if cost == 4:
            index = 2
        elif cost == 3:
            index = 1
        else:
            index = 0
        _score = 0
        for i in v:
            _phantom_value = phantom_main_value_map[i][index]
            if "%" in _phantom_value:
                _phantom_value = _phantom_value.replace("%", "")
            _phantom_value = float(_phantom_value)
            _score += main_props.get(str(cost)).get(i, 0) * _phantom_value

        score.append(round(_score, 2))

    return score


def read_calc_json_files(directory):
    files = directory.rglob("calc*.json")

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = msgjson.decode(f.read())

                skill_weight = data["skill_weight"]
                jineng = max(skill_weight)
                sub_max = calc_sub_max_score(
                    data["max_sub_props"], data["sub_props"], jineng, skill_weight
                )
                main_max = calc_main_max_score(
                    data["max_main_props"], data["main_props"]
                )
                score_max = [round(sub_max + i, 2) for i in main_max]
                logger.info(
                    f"{file.parents[0].name}/{file.name} - 技能分: {jineng} - "
                    f"副词条最大: {sub_max} - "
                    f"主词条最大: {main_max} - "
                    f"总词条分数：{score_max}"
                )
                data["score_max"] = score_max
                data["total_grade"] = [0, 0.48, 0.6, 0.7, 0.78, 0.84]
                data["props_grade"] = [
                    [0, 0.48, 0.6, 0.7, 0.78, 0.84],
                    [0, 0.48, 0.6, 0.7, 0.78, 0.84],
                    [0, 0.48, 0.6, 0.7, 0.78, 0.84],
                ]
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.exception(f"Error decoding {file}", e)


if __name__ == "__main__":
    read_calc_json_files(MAP_PATH)
