from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils.database.models import WavesBind, WavesUser
from ..utils.hint import BIND_UID_HINT
from ..utils.waves_api import waves_api
from ..utils.waves_prefix import PREFIX

waves_daily_info = SV('waves查询体力')


@waves_daily_info.on_fullmatch(
    (
        f'{PREFIX}每日',
        f'{PREFIX}mr',
        f'{PREFIX}实时便笺',
        f'{PREFIX}便笺',
        f'{PREFIX}便签',
    )
)
async def send_daily_info_pic(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[waves每日信息]')
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    await bot.logger.info(f'[waves每日信息]QQ号: {user_id} UID: {uid}')

    ck = await WavesUser.get_user_cookie_by_uid(uid)
    if not uid:
        return await bot.send(BIND_UID_HINT)

    flag, game_info = await waves_api.get_game_info(ck)
    if not flag:
        return await bot.send(game_info)

    await bot.send('Waves每日信息功能正在开发中，敬请期待！')
