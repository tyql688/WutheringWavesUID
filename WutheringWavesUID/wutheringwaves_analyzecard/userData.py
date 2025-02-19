import json
from typing import Any, Dict, Union, Generator

import aiofiles

from gsuid_core.logger import logger

from ..wutheringwaves_charinfo.draw_char_card import generate_online_role_detail
from ..utils.api.model import RoleDetailData
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH


async def save_card_dict_to_json(result_dict):
    
    # 使用json格式输出
    print(json.dumps(result_dict, indent=2, ensure_ascii=False))

    char_id = "1506" # 菲比 F:\CodeAPP\QQBot\gsuid_core\gsuid_core\plugins\WutheringWavesUID\WutheringWavesUID\utils\map\detail_json\char\1506.json
    resuilt = await generate_online_role_detail(char_id)
    print(resuilt)



async def get_all_role_detail_info_list(
    uid: str,
) -> Union[Generator[RoleDetailData, Any, None], None]:
    path = PLAYER_PATH / uid / "rawData.json"
    if not path.exists():
        return None
    try:
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            player_data = json.loads(await f.read())
    except Exception as e:
        logger.exception(f"get role detail info failed {path}:", e)
        path.unlink(missing_ok=True)
        return None

    return iter(RoleDetailData(**r) for r in player_data)


async def get_all_role_detail_info(uid: str) -> Union[Dict[str, RoleDetailData], None]:
    _all = await get_all_role_detail_info_list(uid)
    if not _all:
        return None
    return {r.role.roleName: r for r in _all}
