import re

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .darw_rank_card import draw_rank_img
from .draw_bot_rank_card import draw_bot_rank_img
from .draw_all_rank_card import draw_all_rank_card
from ..wutheringwaves_config import WutheringWavesConfig

sv_waves_rank_list = SV("ww角色排行")
sv_waves_rank_all_list = SV("ww角色总排行", priority=1)
sv_waves_rank_bot_list = SV("ww角色bot排行", priority=1)


@sv_waves_rank_list.on_regex("^[\u4e00-\u9fa5]+(?:排行|排名)$", block=True)
async def send_rank_card(bot: Bot, ev: Event):
    # 正则表达式
    match = re.search(r"(?P<char>[\u4e00-\u9fa5]+)(?:排行|排名)", ev.raw_text)
    if not match:
        return
    ev.regex_dict = match.groupdict()
    char = match.group("char")

    if not ev.group_id:
        return await bot.send("请在群聊中使用")

    if not char:
        return

    rank_type = "伤害"
    if "评分" in char:
        rank_type = "评分"
    char = char.replace("伤害", "").replace("评分", "")

    im = await draw_rank_img(bot, ev, char, rank_type)

    if isinstance(im, str):
        at_sender = True if ev.group_id else False
        await bot.send(im, at_sender)
    if isinstance(im, bytes):
        await bot.send(im)

@sv_waves_rank_bot_list.on_regex("^[\u4e00-\u9fa5]+(?:bot排行|bot排名)$", block=True)
async def send_bot_rank_card(bot: Bot, ev: Event):
    botData = WutheringWavesConfig.get_config("botData").data
    if not botData:
        return await bot.send("[鸣潮] 未开启bot排行")
    # 正则表达式
    match = re.search(
        r"(?P<char>[\u4e00-\u9fa5]+)(?:bot排行|bot排名)",
        ev.raw_text,
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    char = match.group("char")

    if not char:
        return

    rank_type = "伤害"
    if "评分" in char:
        rank_type = "评分"
    char = char.replace("伤害", "").replace("评分", "")

    im = await draw_bot_rank_img(bot, ev, char, rank_type)

    if isinstance(im, str):
        at_sender = True if ev.group_id else False
        await bot.send(im, at_sender)
    if isinstance(im, bytes):
        await bot.send(im)

@sv_waves_rank_all_list.on_regex(
    "^[\u4e00-\u9fa5]+(?:总排行|总排名)(\d+)?$", block=True
)
async def send_all_rank_card(bot: Bot, ev: Event):
    # 正则表达式
    match = re.search(
        r"(?P<char>[\u4e00-\u9fa5]+)(?:总排行|总排名)(?P<pages>(\d+))?",
        ev.raw_text,
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    char = match.group("char")
    pages = match.group("pages")

    if not char:
        return

    if pages:
        pages = int(pages)
    else:
        pages = 1

    if pages > 5:
        pages = 5
    elif pages < 1:
        pages = 1

    rank_type = "伤害"
    if "评分" in char:
        rank_type = "评分"
    char = char.replace("伤害", "").replace("评分", "")

    im = await draw_all_rank_card(bot, ev, char, rank_type, pages)

    if isinstance(im, str):
        at_sender = True if ev.group_id else False
        await bot.send(im, at_sender)
    if isinstance(im, bytes):
        await bot.send(im)
