from pathlib import Path
from typing import List

from msgspec import json as msgjson

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .draw_char_card import draw_char_detail_img
from ..utils.api.api import SERVER_ID
from ..utils.api.model import RoleList
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103, WAVES_CODE_102
from ..utils.hint import error_reply
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.waves_api import waves_api
from ..utils.waves_prefix import PREFIX

waves_get_char_info = SV('waves获取面板')
waves_char_detail = SV(f'waves角色面板')


@waves_get_char_info.on_fullmatch(
    (
        f'{PREFIX}刷新面板',
        f'{PREFIX}强制刷新',
    )
)
async def send_card_info(bot: Bot, ev: Event):
    user_id = ev.at if ev.at else ev.user_id

    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    # user = await WavesUser.get_user_by_attr(user_id, ev.bot_id, 'uid', str(waves_uid))
    # if not user:
    #     return await bot.send(hint.error_reply(code=WAVES_CODE_102))

    ck = await waves_api.get_ck(uid)
    if not ck:
        return await bot.send(error_reply(WAVES_CODE_102))

    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(uid, ck, SERVER_ID)
    if not succ:
        return await bot.send(role_info)

    waves_datas = []
    role_info = RoleList(**role_info)
    for r in role_info.roleList:
        succ, role_detail_info = await waves_api.get_role_detail_info(r.roleId, uid, ck, SERVER_ID)
        if not succ or role_detail_info['role'] is None or role_detail_info['level'] is None:
            continue
        if role_detail_info['phantomData']['cost'] == 0:
            role_detail_info['phantomData']['equipPhantomList'] = None
        waves_datas.append(role_detail_info)

    await save_card_info(uid, waves_datas)

    msg = f'[鸣潮] 刷新完成！本次刷新{len(waves_datas)}个角色!'
    msg += f'\n刷新角色列表:{",".join([i["role"]["roleName"] for i in waves_datas])}'
    return await bot.send(msg)


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


@waves_char_detail.on_prefix((f'{PREFIX}角色面板', f'{PREFIX}查询'))
async def send_char_detail_msg(bot: Bot, ev: Event):
    char = ev.text.strip(' ')
    logger.info(f'[鸣潮] [角色面板] CHAR: {char}')
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))
    logger.info(f'[鸣潮] [角色面板] UID: {uid}')
    if not char:
        return

    im = await draw_char_detail_img(ev, uid, char)
    return await bot.send(im)
