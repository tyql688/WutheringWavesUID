import json
from typing import Union, Any, Generator, Dict

from .resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.api.model import RoleDetailData


async def get_all_role_detail_info_list(uid: str) -> Union[Generator[RoleDetailData, Any, None], None]:
    path = PLAYER_PATH / uid / "rawData.json"
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        player_data = json.load(f)

    return iter(RoleDetailData(**r) for r in player_data)


async def get_all_role_detail_info(uid: str) -> Union[Dict[str, RoleDetailData], None]:
    _all = await get_all_role_detail_info_list(uid)
    if not _all:
        return None
    return {r.role.roleName: r for r in _all}
