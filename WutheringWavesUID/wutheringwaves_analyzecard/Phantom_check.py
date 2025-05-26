from gsuid_core.logger import logger
from pathlib import Path
import asyncio


# change from utils.map.calc_score_script.py
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

# 1, 3, 4 主词条 max value
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


async def exist_attribute_prop(name: str = "") -> bool:
    TEXT_PATH = Path(__file__).parent.parent / "utils" / "texture2d" / "attribute_prop" 
    file_path = Path(TEXT_PATH) / f"attr_prop_{name}.png"
    try:
        return await asyncio.to_thread(file_path.exists)
    except Exception as e:
        logger.error(f"[鸣潮][dc卡片识别]文件检查异常: {name}: {e}")
        return False

def get_props(phantom):
        props = []
        if phantom.get("mainProps"):
            props.extend(phantom.get("mainProps"))
        if phantom.get("subProps"):
            props.extend(phantom.get("subProps"))

        return props

class PhantomValidator:
    def __init__(self, equipPhantomList):
        self.main_value_map = phantom_main_value_map
        self.sub_value_map = phantom_sub_value_map
        self.cost_indices = {1: 0, 3: 1, 4: 2}  # cost到数组索引的映射
        self.equipPhantomList = equipPhantomList

    async def validate_phatom_list(self):
        """验证整个声骸列表"""
        for phantom in self.equipPhantomList:
            if phantom and phantom.get("phantomProp"):
                    props = get_props(phantom)
                    for _prop in props:
                        name_b = await exist_attribute_prop(_prop.get("attributeName"))
                        if not name_b:
                            logger.info(f"[鸣潮][声骸检验]词条文本检查异常: {_prop.get('attributeName')}")
                            return False, None

            value_b, text = self._validate_phantom(phantom)
            if not value_b:
                logger.info(f"[鸣潮][声骸检验]词条数值检查异常：{text}")
                return False, None
                
        return True, self.equipPhantomList

    def _validate_phantom(self, phantom):
        """验证单个声骸"""
        cost = phantom.get("cost", 0)
        logger.debug(f"[鸣潮][声骸检查]声骸cost: {cost}")
        if cost not in self.cost_indices:
            return False, "cost异常"

        # 主词条校验
        for main_prop in phantom.get("mainProps", []):
            is_valid, corrected = self.validate_main_prop(main_prop, cost)
            if not is_valid:
                return False, corrected
            if corrected:
                main_prop["attributeValue"] = corrected

        # 副词条校验
        for sub_prop in phantom.get("subProps", []):
            is_valid, corrected = self.validate_sub_prop(sub_prop)
            if not is_valid:
                return False, corrected
            if corrected:
                sub_prop["attributeValue"] = corrected
        return True, None

    def _preprocess_value(self, name, value):
        """统一数值格式"""
        is_percent_value = "%" in value
        if name in ["攻击", "生命", "防御"]:
            name = name + "%" if is_percent_value else name
        elif not is_percent_value:
            value = value + "%"
        return name, value

    def validate_main_prop(self, prop, cost):
        """主词条验证"""
        cost_idx = self.cost_indices.get(cost, -1)
        _name = prop["attributeName"]
        _value = prop["attributeValue"]

        # 预处理名称
        name, value = self._preprocess_value(_name, _value)

        if "伤害加成" in _name:
            name = "属性伤害加成"

        # 获取合法值列表
        allowed_values = self.main_value_map.get(name, [])
        if not allowed_values or cost_idx >= len(allowed_values):
            return False, _value

        # 检查该cost是否允许此属性
        allowed_value = allowed_values[cost_idx]
        if allowed_value.replace("%", "") == "0":
            return False, _value  # 该cost不允许此属性

        # 智能缩放检测
        scaled_value = self._detect_scale_error(value, [allowed_value])
        logger.debug(f"[鸣潮][声骸检查]主词条：{_value} -> {scaled_value}  {name}")
        return True, scaled_value  # 强制修正为合法值

    def validate_sub_prop(self, prop):
        """副词条验证"""
        _name = prop["attributeName"]
        _value = prop["attributeValue"]

        # 预处理名称
        name, value = self._preprocess_value(_name, _value)

        # 获取可能的数值类型
        allowed_values = self.sub_value_map.get(name, [])
        if not allowed_values:
            return False, _value

        # 智能缩放检测
        scaled_value = self._detect_scale_error(value, allowed_values)

        # 寻找最近合法值
        closest = self._find_closest_sub_value(scaled_value, allowed_values)
        logger.debug(f"[鸣潮][声骸检查]副词条：{_value} -> {closest}  {name}")
        return True, closest

    def _detect_scale_error(self, value, allowed_values):
        """检测10倍缩放错误（如86%→8.6%）"""
        if "%" in value:
            num_str = value.replace("%", "")
            try:
                num = float(num_str)
                max_allowed = max(float(v.replace("%", "")) for v in allowed_values)
                while num > max_allowed:  # 缩放阈值 0倍
                    scaled = num / 10.0   # 正常情况下scaled不被定义，走except
                    num = scaled
                return f"{scaled:.2f}%"
            except Exception as e:
                logger.debug(f"[鸣潮][声骸检查]无法缩放值: {value}与阈值: {allowed_values}，错误信息: {e}")
                pass
        return value

    def _find_closest_sub_value(self, value, allowed_values):
        """寻找最近的合法副词条值"""

        def to_float(v):
            return float(v.replace("%", "")) if "%" in v else float(v)

        try:
            target = to_float(value)
            allowed_floats = [to_float(v) for v in allowed_values]
            closest = min(allowed_floats, key=lambda x: abs(x - target))
            # 返回原始字符串格式
            for v in allowed_values:
                if to_float(v) == closest:
                    return v
        except Exception as e:
            logger.debug(f"[鸣潮][声骸检查]无法寻找阈值: {allowed_values}中的值: {value}，错误信息: {e}")
            return allowed_values[0]  # 兜底返回第一个值
