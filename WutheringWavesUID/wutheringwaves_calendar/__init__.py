from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .draw_calendar_card import draw_calendar_img
from ..wutheringwaves_config import PREFIX

sv_waves_calendar = SV('waves日历')


@sv_waves_calendar.on_fullmatch(
    (f'{PREFIX}个人日历', f'{PREFIX}日历'), block=True
)
async def send_waves_calendar_pic(bot: Bot, ev: Event):
    # at_sender = True if ev.group_id else False
    # user_id = ev.at if ev.at else ev.user_id
    # uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    # if not uid:
    #     return await bot.send(error_reply(WAVES_CODE_103), at_sender)
    uid = ""
    im = await draw_calendar_img(ev, uid)
    return await bot.send(im)
