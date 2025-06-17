import asyncio
import json
from typing import Dict, List, Optional, Union

import aiofiles

from gsuid_core.logger import logger
from gsuid_core.models import Event

from ..utils.api.model import AccountBaseInfo, RoleList
from ..utils.error_reply import WAVES_CODE_101, WAVES_CODE_102, WAVES_CODE_999
from ..utils.expression_ctx import WavesCharRank, get_waves_char_rank
from ..utils.hint import error_reply
from ..utils.queues.const import QUEUE_SCORE_RANK
from ..utils.queues.queues import put_item
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.util import get_version
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import WutheringWavesConfig
from . import waves_card_cache
from .resource.constant import SPECIAL_CHAR_INT_ALL


async def send_card(
    uid: str,
    user_id: str,
    save_data: List,
    is_self_ck: bool = False,
    token: Optional[str] = "",
    role_info: Optional[RoleList] = None,
):
    waves_char_rank: Optional[List[WavesCharRank]] = None

    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if WavesToken:
        waves_char_rank = await get_waves_char_rank(uid, save_data, True)

    await waves_card_cache.save_card(
        uid, save_data, user_id, waves_char_rank, is_self_ck, token
    )

    if is_self_ck and token and waves_char_rank and WavesToken and role_info:
        if len(role_info.roleList) != len(save_data):
            logger.warning(
                f"角色数量不一致，role_info.roleNum:{len(role_info.roleList)} != waves_char_rank:{len(save_data)}"
            )
            return
        succ, account_info = await waves_api.get_base_info(uid, token=token)
        if not succ:
            return account_info
        account_info = AccountBaseInfo.model_validate(account_info)
        if account_info.roleNum != len(save_data):
            logger.warning(
                f"角色数量不一致，role_info.roleNum:{account_info.roleNum} != waves_char_rank:{len(save_data)}"
            )
            return
        metadata = {
            "user_id": user_id,
            "waves_id": f"{account_info.id}",
            "kuro_name": account_info.name,
            "version": get_version(),
            "char_info": [r.to_rank_dict() for r in waves_char_rank],
            "role_num": account_info.roleNum,
        }
        await put_item(QUEUE_SCORE_RANK, metadata)


async def save_card_info(
    uid: str,
    waves_data: List,
    waves_map: Optional[Dict] = None,
    user_id: str = "",
    is_self_ck: bool = False,
    token: str = "",
    role_info: Optional[RoleList] = None,
):
    if len(waves_data) == 0:
        return
    _dir = PLAYER_PATH / uid
    _dir.mkdir(parents=True, exist_ok=True)
    path = _dir / "rawData.json"

    old_data = {}
    if path.exists():
        try:
            async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
                old = json.loads(await f.read())
                old_data = {d["role"]["roleId"]: d for d in old}
        except Exception as e:
            logger.exception(f"save_card_info get failed {path}:", e)
            path.unlink(missing_ok=True)

    #
    refresh_update = {}
    refresh_unchanged = {}
    for item in waves_data:
        role_id = item["role"]["roleId"]

        if role_id in SPECIAL_CHAR_INT_ALL:
            # 漂泊者预处理
            for piaobo_id in SPECIAL_CHAR_INT_ALL:
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

    await send_card(uid, user_id, save_data, is_self_ck, token, role_info)

    try:
        async with aiofiles.open(path, "w", encoding="utf-8") as file:
            await file.write(json.dumps(save_data, ensure_ascii=False))
    except Exception as e:
        logger.exception(f"save_card_info save failed {path}:", e)

    if waves_map:
        waves_map["refresh_update"] = refresh_update
        waves_map["refresh_unchanged"] = refresh_unchanged


async def refresh_char(
    ev: Event,
    uid: str,
    user_id: str,
    ck: Optional[str] = None,  # type: ignore
    waves_map: Optional[Dict] = None,
    is_self_ck: bool = False,
) -> Union[str, List]:
    waves_datas = []
    if not ck:
        is_self_ck, ck = await waves_api.get_ck_result(uid, user_id, ev.bot_id)
    if not ck:
        return error_reply(WAVES_CODE_102)
    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(uid, ck)
    if not succ:
        if isinstance(role_info, str):
            return role_info
        else:
            return error_reply(WAVES_CODE_999)

    try:
        role_info = RoleList.model_validate(role_info)
    except Exception as e:
        logger.exception(f"{uid} 角色信息解析失败", e)
        msg = f"鸣潮特征码[{uid}]获取数据失败\n1.是否注册过库街区\n2.库街区能否查询当前鸣潮特征码数据"
        return msg

    async def limited_get_role_detail_info(role_id, uid, ck):
        async with semaphore:
            return await waves_api.get_role_detail_info(role_id, uid, ck)

    semaphore = asyncio.Semaphore(value=len(role_info.roleList) // 2)
    if is_self_ck:
        tasks = [
            limited_get_role_detail_info(str(r.roleId), uid, ck)
            for r in role_info.roleList
        ]
    else:
        if role_info.showRoleIdList:
            tasks = [
                limited_get_role_detail_info(str(r), uid, ck)
                for r in role_info.showRoleIdList
            ]
        else:
            tasks = [
                limited_get_role_detail_info(str(r.roleId), uid, ck)
                for r in role_info.roleList
            ]
    results = await asyncio.gather(*tasks)

    charId2chainNum: Dict[int, int] = {
        r.roleId: r.chainUnlockNum
        for r in role_info.roleList
        if isinstance(r.chainUnlockNum, int)
    }
    # 处理返回的数据
    for succ, role_detail_info in results:
        if (
            not succ
            or not isinstance(role_detail_info, dict)
            or "role" not in role_detail_info
            or role_detail_info["role"] is None
            or "level" not in role_detail_info
            or role_detail_info["level"] is None
        ):
            continue
        if role_detail_info["phantomData"]["cost"] == 0:
            role_detail_info["phantomData"]["equipPhantomList"] = None
        try:
            # 扰我道心 难道谐振几阶还算不明白吗
            del role_detail_info["weaponData"]["weapon"]["effectDescription"]
        except Exception as _:
            pass

        # 修正共鸣链
        try:
            role_id = role_detail_info["role"]["roleId"]
            for i in role_detail_info["chainList"]:
                if i["order"] <= charId2chainNum[role_id]:
                    i["unlocked"] = True
                else:
                    i["unlocked"] = False
        except Exception as e:
            logger.exception(f"{uid} 共鸣链修正失败", e)

        waves_datas.append(role_detail_info)

    await save_card_info(
        uid,
        waves_datas,
        waves_map,
        user_id,
        is_self_ck=is_self_ck,
        token=ck,
        role_info=role_info,
    )

    if not waves_datas:
        return error_reply(WAVES_CODE_101)

    return waves_datas
