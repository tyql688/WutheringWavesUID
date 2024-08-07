from pathlib import Path

from msgspec import json as msgjson

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils import hint
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import WAVES_CODE_102, WAVES_CODE_203, WAVES_CODE_204
from ..utils.hint import BIND_UID_HINT
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.tap_api import tap_api
from ..utils.waves_prefix import PREFIX

waves_get_char_info = SV('waves获取面板')


@waves_get_char_info.on_command(f'{PREFIX}强制刷新')
async def send_card_info(bot: Bot, ev: Event):
    user_id = ev.at if ev.at else ev.user_id

    waves_uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not waves_uid:
        return await bot.send(BIND_UID_HINT)

    user_list = await WavesUser.select_data_list(user_id=user_id, bot_id=ev.bot_id)
    if not user_list:
        return await bot.send(hint.error_reply(code=WAVES_CODE_102))

    user = await WavesUser.get_user_by_attr(user_id, ev.bot_id, 'uid', str(waves_uid))
    if not user or not user.tap_uid:
        return await bot.send(hint.error_reply(code=WAVES_CODE_203))

    await bot.logger.info(f'[{PREFIX}强制刷新]uid: {waves_uid} tap_uid: {user.tap_uid}')
    waves_datas = await tap_api.get_all_role_info(user.tap_uid)
    if not waves_datas:
        return await bot.send(hint.error_reply(code=WAVES_CODE_204))
    await save_card_info(user_id, waves_uid, user.tap_uid, waves_datas)

    return await bot.send('强制刷新成功')


async def save_card_info(user_id: str, uid: str, tap_uid: str, waves_datas: dict):
    save_path = PLAYER_PATH
    path = save_path / uid
    path.mkdir(parents=True, exist_ok=True)
    with Path.open(path / "rawData.json", "wb") as file:
        file.write(msgjson.format(msgjson.encode(waves_datas), indent=4))
