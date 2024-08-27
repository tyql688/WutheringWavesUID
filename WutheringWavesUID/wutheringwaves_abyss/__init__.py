from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from ..wutheringwaves_abyss.draw_abyss_card import draw_abyss_img
from ..wutheringwaves_config import PREFIX

sv_waves_abyss = SV('waves查询深渊')


@sv_waves_abyss.on_command(
    (
        f'{PREFIX}查询深渊',
        f'{PREFIX}sy',
        f'{PREFIX}深渊',
    ),
    block=True,
)
async def send_waves_abyss_info(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[鸣潮查询深渊信息]')

    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))
    await bot.logger.info(f'[鸣潮查询深渊信息]user_id:{user_id} uid: {uid}')

    im = await draw_abyss_img(ev, uid)
    return await bot.send(im)
