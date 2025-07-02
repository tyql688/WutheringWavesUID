import math
from pathlib import Path
from typing import Dict, List, Union

from msgspec import json as msgjson

from gsuid_core.logger import logger

from ..utils.api.model import Props
from .expression_evaluator import find_first_matching_expression
from .image import SPECIAL_GOLD, WAVES_MOLTEN, WAVES_SIERRA, WAVES_VOID
from .map.calc_score_script import phantom_sub_value_map as ph_sub_map
from .resource.constant import ID_FULL_CHAR_NAME

MAP_PATH = Path(__file__).parent / "map/character"

score_interval = ["c", "b", "a", "s", "ss", "sss"]
fix_max_score = 50


def get_calc_map(ctx: Dict, char_name: str, char_id: Union[int, str]):
    if str(char_id) in ID_FULL_CHAR_NAME:
        char_name = ID_FULL_CHAR_NAME[str(char_id)]
    char_path = MAP_PATH / char_name
    if not char_path.is_dir():
        char_path = MAP_PATH / "default"

    def check_conditions(file_name):
        condition_path = char_path / file_name
        if condition_path.exists():
            with open(condition_path, "r", encoding="utf-8") as f:
                expressions = msgjson.decode(f.read())
            return find_first_matching_expression(ctx, expressions)
        return None

    # 先检查用户条件，然后是默认条件
    calc_json_path = (
        check_conditions("condition-user.json")
        or check_conditions("condition.json")
        or "calc.json"
    )
    logger.debug(f"{char_name} [匹配文件]: {char_path.name}/{calc_json_path}")
    with open(char_path / calc_json_path, "r", encoding="utf-8") as f:
        return msgjson.decode(f.read())


def calc_phantom_entry(index, prop, cost: int, calc_map):
    skill_weight = calc_map.get("skill_weight", [])
    if not skill_weight:
        skill_weight = [0, 0, 0, 0]
    score = 0
    main_props = calc_map["main_props"]
    sub_pros = calc_map["sub_props"]
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
    elif prop.attributeName == "防御":
        if "%" in prop.attributeValue:
            score += pros_temp.get("防御%", 0) * value
        else:
            score += pros_temp.get("防御", 0) * value
    elif prop.attributeName == "普攻伤害加成":
        score += pros_temp.get("技能伤害加成", 0) * skill_weight[0] * value
    elif prop.attributeName == "重击伤害加成":
        score += pros_temp.get("技能伤害加成", 0) * skill_weight[1] * value
    elif prop.attributeName == "共鸣技能伤害加成":
        score += pros_temp.get("技能伤害加成", 0) * skill_weight[2] * value
    elif prop.attributeName == "共鸣解放伤害加成":
        score += pros_temp.get("技能伤害加成", 0) * skill_weight[3] * value
    elif prop.attributeName[0:2] in ["冷凝", "衍射", "导电", "热熔", "气动", "湮灭"]:
        score += pros_temp.get("属性伤害加成", 0) * value
    else:
        score += pros_temp.get(prop.attributeName, 0) * value

    max_score, props_grade = get_max_score(cost, calc_map)
    percent_score = score / max_score
    final_score = math.floor(percent_score * fix_max_score * 100) / 100
    return score, final_score


def get_max_score(cost, calc_map):
    if cost == 1:
        max_score = calc_map["score_max"][0]
        props_grade = calc_map["props_grade"][0]
    elif cost == 3:
        max_score = calc_map["score_max"][1]
        props_grade = calc_map["props_grade"][1]
    else:
        max_score = calc_map["score_max"][2]
        props_grade = calc_map["props_grade"][2]

    return max_score, props_grade


def calc_phantom_score(
    char_name: str, prop_list: List[Props], cost: int, calc_map: Union[Dict, None]
) -> tuple[int, str]:
    if not calc_map:
        return 0, "c"

    score = 0
    for index, prop in enumerate(prop_list):
        _score, _ = calc_phantom_entry(index, prop, cost, calc_map)
        score += _score

    max_score, props_grade = get_max_score(cost, calc_map)
    percent_score = score / max_score

    _temp = 0
    for index, _temp_per in enumerate(props_grade):
        if percent_score >= _temp_per:
            _temp = index

    final_score = math.floor(percent_score * fix_max_score * 100) / 100
    score_level = score_interval[_temp]
    # logger.debug(f"{char_name} [声骸评分]: {final_score} [声骸评分等级]: {score_level}")
    return final_score, score_level


def get_total_score_bg(char_name: str, score: int, calc_map: Union[Dict, None]):
    if not calc_map:
        return "c"

    ratio = score / 250
    _temp = 0
    for index, _score in enumerate(calc_map["total_grade"]):
        if ratio >= _score:
            _temp = index
    score_level = score_interval[_temp]
    logger.debug(
        f"{char_name} [声骸评分]: {score} [总声骸评分等级]: {score_level} [总声骸评分系数]: {ratio:.2f}"
    )
    return score_level


def get_valid_color(name, value, calc_map: Union[Dict, None]):
    name_color = (255, 255, 255)
    num_color = (255, 255, 255)
    name = name.replace("百分比", "")
    if not calc_map:
        return name_color, num_color
    _temp = calc_map["grade"]
    flag = False
    if "valid_s" in _temp and name in _temp["valid_s"]:
        name_color = SPECIAL_GOLD
        num_color = SPECIAL_GOLD
        flag = True
    if "valid_a" in _temp and name in _temp["valid_a"]:
        name_color = WAVES_VOID
        num_color = WAVES_VOID
        flag = True
    if "valid_b" in _temp and name in _temp["valid_b"]:
        name_color = WAVES_SIERRA
        num_color = WAVES_SIERRA
        flag = True

    if flag:
        if name in ph_sub_map and ph_sub_map[name][-1] == value:
            num_color = WAVES_MOLTEN
        elif name + "%" in ph_sub_map and ph_sub_map[name + "%"][-1] == value:
            num_color = WAVES_MOLTEN

    return name_color, num_color
