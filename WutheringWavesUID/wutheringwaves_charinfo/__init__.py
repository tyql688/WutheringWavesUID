import re

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .draw_char_card import draw_char_detail_img, draw_char_score_img
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from ..utils.waves_prefix import PREFIX

waves_new_get_char_info = SV('waves新获取面板', priority=3)
waves_new_char_detail = SV(f'waves新角色面板', priority=4)
waves_char_detail = SV(f'waves角色面板', priority=5)


@waves_new_get_char_info.on_fullmatch(
    (
        f'{PREFIX}刷新面板',
        f'{PREFIX}更新面板',
        f'{PREFIX}强制刷新',
    ),
    block=True
)
async def send_card_info(bot: Bot, ev: Event):
    user_id = ev.at if ev.at else ev.user_id

    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    from .draw_refresh_char_card import draw_refresh_char_detail_img
    msg = await draw_refresh_char_detail_img(bot, ev, user_id, uid)
    return await bot.send(msg)


@waves_char_detail.on_prefix((f'{PREFIX}角色面板', f'{PREFIX}查询'))
async def send_char_detail_msg(bot: Bot, ev: Event):
    char = ev.text.strip(' ')
    logger.debug(f'[鸣潮] [角色面板] CHAR: {char}')
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))
    logger.debug(f'[鸣潮] [角色面板] UID: {uid}')
    if not char:
        return

    im = await draw_char_detail_img(ev, uid, char)
    return await bot.send(im)


@waves_new_char_detail.on_regex(rf'{PREFIX}(\d+)?[\u4e00-\u9fa5]+(?:面板|伤害\d+)', block=True)
async def send_char_detail_msg2(bot: Bot, ev: Event):
    match = re.search(
        rf'{PREFIX}(?P<waves_id>\d+)?(?P<char>[\u4e00-\u9fa5]+)(?:面板|伤害(?P<damage>\d+))',
        ev.raw_text
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    waves_id = ev.regex_dict.get("waves_id")
    char = ev.regex_dict.get("char")
    damage = ev.regex_dict.get("damage")

    if waves_id and len(waves_id) != 9:
        return

    if damage:
        char = f'{char}{damage}'

    logger.debug(f'[鸣潮] [角色面板] CHAR: {char}')
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))
    logger.debug(f'[鸣潮] [角色面板] UID: {uid}')
    if not char:
        return

    im = await draw_char_detail_img(ev, uid, char, waves_id)
    at_sender = False
    if isinstance(im, str) and ev.group_id:
        at_sender = True
    return await bot.send(im, at_sender)


@waves_new_char_detail.on_regex(rf'{PREFIX}(\d+)?[\u4e00-\u9fa5]+(?:权重)', block=True)
async def send_char_detail_msg2(bot: Bot, ev: Event):
    match = re.search(
        rf'{PREFIX}(?P<waves_id>\d+)?(?P<char>[\u4e00-\u9fa5]+)(?:权重)',
        ev.raw_text
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    waves_id = ev.regex_dict.get("waves_id")
    char = ev.regex_dict.get("char")

    if waves_id and len(waves_id) != 9:
        return

    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))
    if not char:
        return

    im = await draw_char_score_img(ev, uid, char, waves_id)
    at_sender = False
    if isinstance(im, str) and ev.group_id:
        at_sender = True
    return await bot.send(im, at_sender)
