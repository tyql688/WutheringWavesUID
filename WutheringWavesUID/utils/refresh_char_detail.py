import asyncio
from pathlib import Path
from typing import List, Union, Dict

from msgspec import json as msgjson

from gsuid_core.logger import logger
from .resource.constant import SPECIAL_CHAR_INT
from .simple_async_cache_card import card_cache
from ..utils.api.model import RoleList
from ..utils.error_reply import WAVES_CODE_102, WAVES_CODE_101
from ..utils.hint import error_reply
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.waves_api import waves_api


async def save_card_info(uid: str, waves_data: List, waves_map: Dict = None):
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

    #
    refresh_update = {}
    refresh_unchanged = {}
    for item in waves_data:
        role_id = item['role']['roleId']

        if role_id in SPECIAL_CHAR_INT:
            # 漂泊者预处理
            for piaobo_id in SPECIAL_CHAR_INT[role_id]:
                old = old_data.get(piaobo_id)
                if not old:
                    continue
                if piaobo_id != role_id:
                    del old_data[piaobo_id]

        old = old_data.get(role_id)
        if old != item:
            refresh_update[role_id] = item
        else:
            refresh_unchanged[role_id] = item

        old_data[role_id] = item

    save_data = list(old_data.values())
    # 保存缓存
    await card_cache.set(uid, save_data)

    with Path.open(path, "wb") as file:
        file.write(msgjson.format(msgjson.encode(save_data)))

    if waves_map:
        waves_map['refresh_update'] = refresh_update
        waves_map['refresh_unchanged'] = refresh_unchanged


async def refresh_char(uid: str, user_id, ck: str = '', waves_map: Dict = None) -> Union[str, List]:
    waves_datas = []
    if not ck:
        ck = await waves_api.get_ck(uid, user_id)
    if not ck:
        return error_reply(WAVES_CODE_102)
    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(uid, ck)
    if not succ:
        return role_info
    try:
        role_info = RoleList(**role_info)
    except Exception as e:
        logger.exception(f'{uid} 角色信息解析失败', e)
        msg = f"鸣潮特征码[{uid}]获取数据失败\n1.是否注册过库街区\n2.库街区能否查询当前鸣潮特征码数据"
        return msg

    # 改为异步处理
    tasks = [
        waves_api.get_role_detail_info(r.roleId, uid, ck) for r in role_info.roleList
    ]
    results = await asyncio.gather(*tasks)

    # 处理返回的数据
    for succ, role_detail_info in results:
        if (not succ
            or 'role' not in role_detail_info
            or role_detail_info['role'] is None
            or 'level' not in role_detail_info
            or role_detail_info['level'] is None):
            continue
        if role_detail_info['phantomData']['cost'] == 0:
            role_detail_info['phantomData']['equipPhantomList'] = None
        try:
            # 扰我道心 难道谐振几阶还算不明白吗
            del role_detail_info['weaponData']['weapon']['effectDescription']
        except Exception as _:
            pass
        waves_datas.append(role_detail_info)

    await save_card_info(uid, waves_datas, waves_map)

    if not waves_datas:
        return error_reply(WAVES_CODE_101)

    return waves_datas
