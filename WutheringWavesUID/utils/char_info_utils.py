import json
from typing import Union

from .resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.api.model import RoleDetailData


async def get_all_role_detail_info(uid: str) -> Union[dict[str, RoleDetailData], None]:
    path = PLAYER_PATH / uid / "rawData.json"
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        player_data = json.load(f)

    return {r["role"]["roleName"]: RoleDetailData(**r) for r in player_data}
