from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .draw_waves_stamina import draw_stamina_img
from ..utils.database.models import WavesBind
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_103
from ..utils.waves_prefix import PREFIX

waves_daily_info = SV('waves查询体力')


@waves_daily_info.on_fullmatch(
    (
        f'{PREFIX}每日',
        f'{PREFIX}mr',
        f'{PREFIX}实时便笺',
        f'{PREFIX}便笺',
        f'{PREFIX}便签',
        f'{PREFIX}体力',
    )
)
async def send_daily_info_pic(bot: Bot, ev: Event):
    await bot.logger.info(f'[鸣潮]开始执行[每日信息]: {ev.user_id}')
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])
    return await bot.send(await draw_stamina_img(bot, ev))
