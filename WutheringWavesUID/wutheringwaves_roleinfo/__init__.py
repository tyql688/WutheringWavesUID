from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils.database.models import WavesBind, WavesUser
from ..utils.hint import BIND_UID_HINT
from ..utils.waves_api import waves_api
from ..utils.waves_prefix import PREFIX

waves_role_info = SV('waves查询信息')


@waves_role_info.on_fullmatch(f'{PREFIX}查询', block=True)
async def send_role_info(bot: Bot, ev: Event):
    logger.info('开始执行[Waves查询]')
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    logger.info(f'[Waves查询] user_id: {user_id} UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)

    ck = await WavesUser.get_user_cookie_by_uid(uid)
    if not uid:
        return await bot.send(BIND_UID_HINT)

    flag, game_info = await waves_api.get_game_info(ck)
    if not flag:
        return await bot.send(game_info)

    flag, role_info = await waves_api.get_role_info(game_info['serverId'], uid, ck)
    if not flag:
        return await bot.send(role_info)

    flag, account_info = await waves_api.get_account_info(game_info['serverId'], uid, ck)
    if not flag:
        return await bot.send(account_info)

    await bot.send('Waves查询功能正在开发中，敬请期待！')
