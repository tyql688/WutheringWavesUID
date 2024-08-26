import copy
from pathlib import Path
from typing import List

from msgspec import json as msgjson

from gsuid_core.logger import logger
from ..utils.api.model import Props

MAP_PATH = Path(__file__).parent / "map"

with open(MAP_PATH / "calculate.json", "r", encoding="UTF-8") as f:
    calculate_data = msgjson.decode(f.read())


def calc_phantom_score(char_name: str, prop_list: List[Props], cost: int) -> (int, str):
    rule_map = calculate_data["rule_map"]
    if char_name not in rule_map:
        return 0, "c"

    custom_score = copy.deepcopy(rule_map[char_name]["score_type"])
    score_type = copy.deepcopy(calculate_data["score_type_map"][str(custom_score["type"])])
    score_type.update(custom_score)

    skill_weight = rule_map[char_name].get("skill_weight", [])
    if not skill_weight:
        skill_weight = [0, 0, 0, 0]

    score = 0
    for index, prop in enumerate(prop_list):
        ratio = 1
        if index < 2:
            # 主属性
            ratio = 0.4

        value = prop.attributeValue
        if "%" in prop.attributeValue:
            value = float(value.replace("%", ""))
        else:
            value = float(value)
        if prop.attributeName == "攻击":
            if "%" in prop.attributeValue:
                score += score_type.get("攻击%", 0) * value * ratio
            else:
                score += score_type.get("攻击", 0) * value * ratio
        elif prop.attributeName == "生命":
            if "%" in prop.attributeValue:
                score += score_type.get("生命%", 0) * value * ratio
            else:
                score += score_type.get("生命", 0) * value * ratio
        elif prop.attributeName == "普攻伤害加成":
            score += skill_weight[0] * value * ratio
        elif prop.attributeName == "重击伤害加成":
            score += skill_weight[1] * value * ratio
        elif prop.attributeName == "共鸣技能伤害加成":
            score += skill_weight[2] * value * ratio
        elif prop.attributeName == "共鸣解放伤害加成":
            score += skill_weight[3] * value * ratio
        else:
            score += score_type.get(prop.attributeName, 0) * value * ratio

    if cost == 1:
        max_score = rule_map[char_name]['score_max'][2]
        fix_max_score = calculate_data['score_max'][2]
    elif cost == 3:
        max_score = rule_map[char_name]['score_max'][1]
        fix_max_score = calculate_data['score_max'][1]
    elif cost == 4:
        max_score = rule_map[char_name]['score_max'][0]
        fix_max_score = calculate_data['score_max'][0]

    _temp = 0
    cost_level = rule_map[char_name]['cost_level']
    for index, _score in enumerate(cost_level[str(cost)]):
        if score >= _score:
            _temp = index

    score = round((score / max_score) * fix_max_score, 1)
    score_level = score_type['score_interval'][_temp]
    logger.debug(f"{char_name} [声骸评分]: {score} [声骸评分等级]:{score_level}")
    return score, score_level


def get_total_score_bg(char_name: str, score: int):
    rule_map = calculate_data["rule_map"]
    if char_name not in rule_map:
        return "c"
    custom_score = copy.deepcopy(rule_map[char_name]["score_type"])
    score_type = copy.deepcopy(calculate_data["score_type_map"][str(custom_score["type"])])
    score_type.update(custom_score)
    ratio = score / calculate_data['total_score_max']
    _temp = 0
    for index, _score in enumerate(score_type['score_interval_ratio']):
        if ratio >= _score:
            _temp = index
    score_level = score_type['score_interval'][_temp]
    logger.debug(f"{char_name} [声骸评分]: {score} [总声骸评分等级]:{score_level} [总声骸评分系数]:{ratio:.2f}")
    return score_level


def get_valid_color(char_name: str, attribute_name: str):
    rule_map = calculate_data["rule_map"]
    if char_name not in rule_map:
        return 255, 255, 255
    _temp = rule_map[char_name]
    if "valid_s" in _temp:
        if attribute_name in _temp["valid_s"]:
            return 234, 183, 4
    if "valid_a" in _temp:
        if attribute_name in _temp["valid_a"]:
            return 107, 140, 179

    return 255, 255, 255
