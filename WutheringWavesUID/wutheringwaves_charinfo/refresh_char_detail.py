from pathlib import Path
from typing import List, Union

from msgspec import json as msgjson

from ..utils.api.model import RoleList
from ..utils.error_reply import WAVES_CODE_102
from ..utils.hint import error_reply
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.waves_api import waves_api


async def save_card_info(uid: str, waves_data: List):
    if len(waves_data) == 0:
        return
    _dir = PLAYER_PATH / uid
    _dir.mkdir(parents=True, exist_ok=True)
    path = _dir / "rawData.json"

    old_data = {}
    if path.exists():
        with Path.open(path, "rb") as file:
            old = msgjson.decode(file.read())
            old_data = {d['role']['roleId']: d for d in old}

    for item in waves_data:
        role_id = item['role']['roleId']
        old_data[role_id] = item

    with Path.open(path, "wb") as file:
        file.write(msgjson.format(msgjson.encode(list(old_data.values()))))


async def refresh_char(uid: str, ck: str = '') -> Union[str, List]:
    waves_datas = []
    if not ck:
        ck = await waves_api.get_ck(uid)
    if not ck:
        return error_reply(WAVES_CODE_102)
    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(uid, ck)
    if not succ:
        return role_info

    role_info = RoleList(**role_info)
    for r in role_info.roleList:
        succ, role_detail_info = await waves_api.get_role_detail_info(r.roleId, uid, ck)
        if not succ or role_detail_info['role'] is None or role_detail_info['level'] is None:
            continue
        if role_detail_info['phantomData']['cost'] == 0:
            role_detail_info['phantomData']['equipPhantomList'] = None
        waves_datas.append(role_detail_info)

    await save_card_info(uid, waves_datas)

    return waves_datas
