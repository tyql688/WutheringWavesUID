import json
import time
import aiofiles

from gsuid_core.logger import logger

from ..utils.waves_api import waves_api
from ..utils.api.model import AccountBaseInfo
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH


# creatTime 是为了满足.is_full的逻辑


async def get_user_detail_info(
    uid: str,
) -> AccountBaseInfo:
    path = PLAYER_PATH / uid / "userData.json"
    if not path.exists():
        # 用户数据不存在时返回默认信息
        is_global = waves_api.is_net(uid)
        return AccountBaseInfo(
            name="国际服用户" if is_global else "国服用户",
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
