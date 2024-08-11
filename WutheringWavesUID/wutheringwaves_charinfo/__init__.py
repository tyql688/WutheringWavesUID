from pathlib import Path
from typing import List

from msgspec import json as msgjson

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils import hint
from ..utils.api.api import SERVER_ID
from ..utils.api.model import RoleList
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import WAVES_CODE_102
from ..utils.hint import BIND_UID_HINT
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.waves_api import waves_api
from ..utils.waves_prefix import PREFIX

waves_get_char_info = SV('waves获取面板')


@waves_get_char_info.on_fullmatch(
    (
        f'{PREFIX}刷新面板',
        f'{PREFIX}强制刷新',
    )
)
async def send_card_info(bot: Bot, ev: Event):
    user_id = ev.at if ev.at else ev.user_id

    waves_uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not waves_uid:
        return await bot.send(BIND_UID_HINT)

    user = await WavesUser.get_user_by_attr(user_id, ev.bot_id, 'uid', str(waves_uid))
    if not user:
        return await bot.send(hint.error_reply(code=WAVES_CODE_102))

    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(user.uid, user.cookie, SERVER_ID)
    if not succ:
        return role_info

    waves_datas = []
    role_info = RoleList(**role_info)
    for r in role_info.roleList:
        succ, role_detail_info = await waves_api.get_role_detail_info(r.roleId, user.uid, user.cookie, SERVER_ID)
        if not succ:
            continue
        if role_detail_info['phantomData']['cost'] == 0:
            role_detail_info['phantomData']['equipPhantomList'] = None
        waves_datas.append(role_detail_info)

    await save_card_info(user_id, waves_uid, waves_datas)

    msg = f'[鸣潮] 刷新完成！本次刷新{len(waves_datas)}个角色!'
    msg += f'\n刷新角色列表:{",".join([i["role"]["roleName"] for i in waves_datas])}'
    return await bot.send(msg)


async def save_card_info(user_id: str, uid: str, waves_datas: List):
    path = PLAYER_PATH / uid
    path.mkdir(parents=True, exist_ok=True)
    with Path.open(path / "rawData.json", "wb") as file:
        file.write(msgjson.format(msgjson.encode(waves_datas)))
