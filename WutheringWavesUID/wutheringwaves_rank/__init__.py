import re
import time

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.waves_card_cache import get_user_all_card, refresh_ranks
from ..wutheringwaves_config import WutheringWavesConfig
from .darw_rank_card import draw_rank_img
from .draw_all_rank_card import draw_all_rank_card

sv_waves_rank_list = SV("ww角色排行")
sv_waves_rank_all_list = SV("ww角色总排行", priority=1)
sv_waves_rank_refresh = SV("ww刷新排行", priority=1, pm=1)
# sv_waves_rank_refresh_group = SV(f'ww刷新群排行', pm=3)

CardUseOptions = WutheringWavesConfig.get_config("CardUseOptions").data


@sv_waves_rank_list.on_regex("^[\u4e00-\u9fa5]+(bot)?(?:排行|排名)$", block=True)
async def send_rank_card(bot: Bot, ev: Event):
    # 正则表达式
    match = re.search(
        r"(?P<char>[\u4e00-\u9fa5]+)(?P<is_bot>bot)?(?:排行|排名)", ev.raw_text
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    char = match.group("char")
    is_bot = match.group("is_bot") == "bot"

    if not WutheringWavesConfig.get_config("BotRank").data:
        is_bot = False

    if not is_bot and not ev.group_id:
        return await bot.send("请在群聊中使用")

    if not char:
        return

    rank_type = "伤害"
    if "评分" in char:
        rank_type = "评分"
    char = char.replace("伤害", "").replace("评分", "")

    im = await draw_rank_img(bot, ev, char, rank_type, is_bot)

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


@sv_waves_rank_refresh.on_fullmatch("刷新全部排行", block=True)
async def refresh_rank_list(bot: Bot, ev: Event):
    if CardUseOptions != "redis缓存":
        await bot.send("当前排行数据存储方式非Redis缓存，不需进行刷新排行")
        return
    await bot.send("正在刷新排行，请耐心稍等...")
    server_all_cards = await get_user_all_card()
    if not server_all_cards:
        return

    a = time.time()
    total = await refresh_ranks(server_all_cards)
    await bot.send(f"恭喜刷新成功\n耗时{time.time() - a:.2f}秒\n刷新总人数: {total}")
