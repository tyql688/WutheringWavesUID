from pathlib import Path
from typing import List

from msgspec import json as msgjson

from gsuid_core.logger import logger
from ..utils.api.model import Props

MAP_PATH = Path(__file__).parent / "map/character"

character_calculate_data = {}
score_interval = [
    "c",
    "b",
    "a",
    "s"
]


def read_calc_json_files(directory):
    files = directory.rglob('calc*.json')

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = msgjson.decode(f.read())

                char_name = file.parents[0].name
                file_name = file.name
                if char_name not in character_calculate_data:
                    character_calculate_data[char_name] = {}

                character_calculate_data[char_name][file_name] = data

        except Exception as e:
            logger.exception(f"Error decoding {file}", e)


read_calc_json_files(MAP_PATH)


def check_calc_map(char_name: str):
    return char_name if char_name in character_calculate_data else "default"


def calc_phantom_score(char_name: str, prop_list: List[Props], cost: int) -> (int, str):
    calc_map = character_calculate_data.get(check_calc_map(char_name), {}).get("calc.json", {})

    if not calc_map:
        return 0, "c"

    skill_weight = calc_map.get("skill_weight", [])
    if not skill_weight:
        skill_weight = [0, 0, 0, 0]

    score = 0
    main_props = calc_map['main_props']
    sub_pros = calc_map['sub_props']
    for index, prop in enumerate(prop_list):
        if index < 2:
            # 主属性
            pros_temp = main_props.get(str(cost))
        else:
            pros_temp = sub_pros

        value = prop.attributeValue
        if "%" in prop.attributeValue:
            value = float(value.replace("%", ""))
        else:
            value = float(value)
        if prop.attributeName == "攻击":
            if "%" in prop.attributeValue:
                score += pros_temp.get("攻击%", 0) * value
            else:
                score += pros_temp.get("攻击", 0) * value
        elif prop.attributeName == "生命":
            if "%" in prop.attributeValue:
                score += pros_temp.get("生命%", 0) * value
            else:
                score += pros_temp.get("生命", 0) * value
        elif prop.attributeName == "普攻伤害加成":
            score += pros_temp.get("技能伤害加成", 0) * skill_weight[0] * value
        elif prop.attributeName == "重击伤害加成":
            score += pros_temp.get("技能伤害加成", 0) * skill_weight[1] * value
        elif prop.attributeName == "共鸣技能伤害加成":
            score += pros_temp.get("技能伤害加成", 0) * skill_weight[2] * value
        elif prop.attributeName == "共鸣解放伤害加成":
            score += pros_temp.get("技能伤害加成", 0) * skill_weight[3] * value
        elif prop.attributeName[0:2] in ["冷凝", "衍射", "导电", "热熔", "气动"]:
            score += pros_temp.get("属性伤害加成", 0) * value
        else:
            score += pros_temp.get(prop.attributeName, 0) * value

    fix_max_score = 50
    if cost == 1:
        max_score = calc_map['score_max'][0]
        props_grade = calc_map['props_grade'][0]
    elif cost == 3:
        max_score = calc_map['score_max'][1]
        props_grade = calc_map['props_grade'][1]
    else:
        max_score = calc_map['score_max'][2]
        props_grade = calc_map['props_grade'][2]

    percent_score = score / max_score

    _temp = 0
    for index, _temp_per in enumerate(props_grade):
        if percent_score >= _temp_per:
            _temp = index

    final_score = round(percent_score * fix_max_score, 1)
    score_level = score_interval[_temp]
    logger.debug(f"{char_name} [声骸评分]: {final_score} [声骸评分等级]: {score_level}")
    return final_score, score_level


def get_total_score_bg(char_name: str, score: int):
    calc_map = character_calculate_data.get(check_calc_map(char_name), {}).get("calc.json", {})

    if not calc_map:
        return 0, "c"

    ratio = score / 250
    _temp = 0
    for index, _score in enumerate(calc_map['total_grade']):
        if ratio >= _score:
            _temp = index
    score_level = score_interval[_temp]
    logger.debug(f"{char_name} [声骸评分]: {score} [总声骸评分等级]: {score_level} [总声骸评分系数]: {ratio:.2f}")
    return score_level


def get_valid_color(char_name: str, attribute_name: str):
    calc_map = character_calculate_data.get(check_calc_map(char_name), {}).get("calc.json", {})
    if not calc_map:
        return 255, 255, 255
    _temp = calc_map['grade']
    if "valid_s" in _temp:
        if attribute_name in _temp["valid_s"]:
            return 234, 183, 4
    if "valid_a" in _temp:
        if attribute_name in _temp["valid_a"]:
            return 107, 140, 179

    return 255, 255, 255
