import json
import time
import aiofiles

from gsuid_core.logger import logger

from ..utils.api.model import AccountBaseInfo
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH


# creatTime 是为了满足.is_full的逻辑
# 1 5 6 7 8 9
# 国美欧亚港澳台SEA东南亚

def get_region_by_uid(uid: str) -> str:
    if not uid:
        return "未知"
    
    first_char = uid[0]
    region_map = {
        '1': '国',
        '5': '美',
        '6': '欧',
        '7': '亚',
        '8': '港澳台',
        '9': '东南亚'
    }
    return region_map.get(first_char, "未知")

def get_region_for_rank(uid: str) -> tuple[str, tuple[int, int, int]]:
    """
    返回元组：(显示文本, 背景颜色)
    """
    if not uid:
        return ("未知", (128, 128, 128))  # 灰色
    
    first_char = uid[0]
    region_map = {
        '1': ("国服", (220, 60, 60)),    # 红色系
        '5': ("美服", (60, 100, 220)),   # 蓝色系
        '6': ("欧服", (80, 180, 80)),    # 绿色系
        '7': ("亚服", (220, 140, 60)),   # 橙色系
        '8': ("港澳台", (160, 60, 220)), # 紫色系
        '9': ("SEA", (60, 180, 220))     # 青色系
    }
    return region_map.get(first_char, ("未知", (128, 128, 128)))

async def get_user_detail_info(
    uid: str,
) -> AccountBaseInfo:
    path = PLAYER_PATH / uid / "userData.json"
    if not path.exists():
        # 用户数据不存在时返回默认信息
        iregion = get_region_by_uid(uid)  # 获取用户地区
        return AccountBaseInfo(
            name=f"{iregion}服用户",
            id=uid,
            creatTime=1,  # 固定为1以满足.is_full逻辑
            level=0,
            worldLevel=0,
        )

    try:
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            player_data = json.loads(await f.read())
            return AccountBaseInfo(**player_data)
    except Exception as e:
        logger.exception(f"get user detail info failed {path}:", e)
        path.unlink(missing_ok=True)
        return AccountBaseInfo(name="错误", id=uid, creatTime=1, level=0, worldLevel=0)


async def save_user_info(uid: str, name: str, level=0, worldLevel=0):
    path = PLAYER_PATH / uid / "userData.json"

    # 准备保存的数据
    save_data = {
        "id": uid,
        "name": name,
        "level": level,
        "worldLevel": worldLevel,
        "creatTime": int(time.time()),
    }

    try:
        async with aiofiles.open(path, "w", encoding="utf-8") as file:
            await file.write(json.dumps(save_data, ensure_ascii=False))
    except Exception as e:
        logger.exception(f"save_user_info save failed {path}:", e)
