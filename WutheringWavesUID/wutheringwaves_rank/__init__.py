import re

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .darw_rank_card import draw_rank_img
from ..wutheringwaves_config import PREFIX

sv_waves_rank_list = SV(f'{PREFIX}角色排行')


@sv_waves_rank_list.on_regex(f'{PREFIX}[\u4e00-\u9fa5]+排行', block=True)
async def send_rank_card(bot: Bot, ev: Event):
    if not ev.group_id:
        return await bot.send('请在群聊中使用')

    # 正则表达式
    match = re.search(
        rf'{PREFIX}(?P<char>[\u4e00-\u9fa5]+)排行',
        ev.raw_text
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    char = match.group('char')
    if not char:
        return
    
    rank_type = '伤害'
    if '评分' in char:
        rank_type = '评分'
    char = char.replace('伤害', '').replace('评分', '')

    im = await draw_rank_img(bot, ev, char, rank_type)
    return await bot.send(im)
