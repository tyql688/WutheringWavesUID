import json
import re
from pathlib import Path

from gsuid_core.logger import logger

from .detail_json import DETAIL, SONATA_COST_4_ID, SONATA_COST_3_ID, SONATA_COST_1_ID

PLUGIN_PATH =  Path(__file__).parent.parent
FETTERDETAIL_PATH = PLUGIN_PATH / "utils/map/detail_json/sonata"



async def get_fetterDetail_from_char(char_id) -> dict:
    
    sonata = DETAIL[char_id]['fetterDetail']
    if sonata == "":
        return {}

    return await get_fetterDetail_from_sonata(sonata)

async def get_fetterDetail_from_sonata(sonata) -> dict:
    
    path = FETTERDETAIL_PATH / f"{sonata}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

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
    return echo

async def get_first_echo_id_list(sonata_name):
    phantom_id_list = [
        {"cost": 4, "list": SONATA_COST_4_ID.get(sonata_name, [])},
        {"cost": 3, "list": SONATA_COST_3_ID.get(sonata_name, [])},
        {"cost": 1, "list": SONATA_COST_1_ID.get(sonata_name, [])},
    ]
    logger.debug(f"[鸣潮]获取到{sonata_name}的声骸id列表：{phantom_id_list}")
    return phantom_id_list

async def echo_data_to_cost(char_id, mainProps_first, cost4_counter=0) -> tuple[int, int]:
    """
    根据主词条判断声骸cost并返回适配ID
    
    参数：
        char_name: str - 角色名称
        mainProps_first: dict - 主词条数据，需包含attributeName和attributeValue
        
    返回：
        tuple (echo_id, cost)
    """
    # ---------- 常量定义 ----------
    # 主词条阈值配置 . change from utils.map.calc_score_script.py
    phantom_main_value = [
        {"name": "攻击", "values": ["18%", "30%", "33%"]},
        {"name": "生命", "values": ["22.8%", "30%", "33%"]},
        {"name": "防御", "values": ["18%", "38%", "41.8%"]},
    ]
    phantom_main_value_map = {i["name"]: i["values"] for i in phantom_main_value}
    
    # 属性类型定义
    FOUR_COST_ATTRS = {"暴击", "暴击伤害", "治疗效果加成"}
    THREE_COST_PATTERNS = [r"共鸣效率", r".*伤害加成"]
    BASE_COST_ATTRS = {"攻击", "生命", "防御"}
    
    # 默认ID配置
    ECHO_ID_COST_ONE = 6000054
    ECHO_ID_COST_THREE = 6000050

    # ---------- 初始化 ----------
    key = mainProps_first[0]["attributeName"]
    value = float(mainProps_first[0]["attributeValue"].strip('%'))
    key_little = mainProps_first[1]["attributeName"] # 小词条
    
    # ---------- 获取角色配置 ----------
    try:
        # 获取完整的层级结构
        full_id_list = await get_first_echo_id_list(DETAIL[char_id]['fetterDetail'])
        # 提取 4cost 的列表
        echo_id_list = [echo_id for item in full_id_list if item["cost"] == 4 for echo_id in item["list"]]
    except KeyError as e:
        logger.error(f"[鸣潮]角色配置数据缺失: {e}")
        return ECHO_ID_COST_ONE, 1  # 降级处理
    except FileNotFoundError:
        logger.error(f"[鸣潮]角色{DETAIL[char_id]['name']}配置文件不存在")
        return ECHO_ID_COST_ONE, 1

    # ---------- 4cost分配id逻辑 ----------
    def select_cost4_id():
        """选择cost4的ID（实现44111逻辑）"""
        if len(echo_id_list) >= 2:
            used_idx = cost4_counter % 2  # 在0和1之间循环
            return echo_id_list[used_idx]
        else:
            return echo_id_list[0]

    # 处理4cost属性
    if key in FOUR_COST_ATTRS:
        return select_cost4_id(), 4
    
    # 处理3cost属性（正则匹配）
    if any(re.fullmatch(p, key) for p in THREE_COST_PATTERNS):
        return ECHO_ID_COST_THREE, 3
    
    # 处理基础属性
    if key in BASE_COST_ATTRS:
        try:
            thresholds = phantom_main_value_map[key]
            t1 = float(thresholds[0].strip('%'))
            t2 = float(thresholds[1].strip('%'))
            
            if value > t2:
                return select_cost4_id(), 4
            elif value > t1:
                return ECHO_ID_COST_THREE, 3
            elif key_little == "生命": # 声骸没拉满时
                return ECHO_ID_COST_ONE, 1
            else:
                return ECHO_ID_COST_THREE, 3
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"[鸣潮]阈值处理异常: {e}")
            return ECHO_ID_COST_ONE, 1  # 降级处理
    
    # 未知属性处理
    logger.warning(f"[鸣潮]未知主词条类型: {key}")
    return ECHO_ID_COST_ONE, 1  # 安全降级


