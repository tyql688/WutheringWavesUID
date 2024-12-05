import re

from PIL import Image

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.image.convert import convert_img
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

    im = await draw_char_detail_img(ev, uid, char, user_id)
    return await bot.send(im)


@waves_new_char_detail.on_regex(rf'{PREFIX}(\d+)?[\u4e00-\u9fa5]+(?:面板|伤害\d+)(?:pk|对比|PK|比|比较)?', block=True)
async def send_char_detail_msg2(bot: Bot, ev: Event):
    match = re.search(
        rf'{PREFIX}(?P<waves_id>\d+)?(?P<char>[\u4e00-\u9fa5]+)(?:面板|伤害(?P<damage>\d+))(?P<is_pk>pk|对比|PK|比|比较)?',
        ev.raw_text
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    waves_id = ev.regex_dict.get("waves_id")
    char = ev.regex_dict.get("char")
    damage = ev.regex_dict.get("damage")
    is_pk = ev.regex_dict.get("is_pk") is not None

    if waves_id and len(waves_id) != 9:
        return

    if damage:
        char = f'{char}{damage}'
    if not char:
        return
    logger.debug(f'[鸣潮] [角色面板] CHAR: {char}')

    at_sender = True if ev.group_id else False
    if is_pk:
        if not waves_id and not ev.at:
            logger.info(f'{waves_id} {ev.at}')
            return await bot.send(f'[鸣潮] [角色面板] 角色【{char}】PK需要指定目标玩家!\n', at_sender)

        if ev.at and ev.at == ev.user_id:
            return await bot.send(f'[鸣潮] [角色面板] 角色【{char}】请勿PK自己，请指定目标玩家!\n', at_sender)

        uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
        if not uid:
            return await bot.send(error_reply(WAVES_CODE_103))

        if f"{waves_id}" == uid:
            return await bot.send(f'[鸣潮] [角色面板] 角色【{char}】请勿PK自己，请指定目标玩家!\n', at_sender)

        im1 = await draw_char_detail_img(ev, uid, char, ev.user_id, waves_id=None, need_convert_img=False,
                                         is_force_avatar=True)
        if isinstance(im1, str):
            return await bot.send(im1, at_sender)

        user_id = ev.at if ev.at else ev.user_id
        uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
        if not uid:
            return await bot.send(error_reply(WAVES_CODE_103))
        im2 = await draw_char_detail_img(ev, uid, char, user_id, waves_id, need_convert_img=False)
        if isinstance(im2, str):
            return await bot.send(im2, at_sender)

        # 创建一个新的图片对象
        new_im = Image.new('RGBA', (im1.size[0] + im2.size[0], max(im1.size[1], im2.size[1])))

        # 将两张图片粘贴到新图片对象上
        new_im.paste(im1, (0, 0))
        new_im.paste(im2, (im1.size[0], 0))
        new_im = await convert_img(new_im)
        return await bot.send(new_im)
    else:
        user_id = ev.at if ev.at else ev.user_id
        uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
        if not uid:
            return await bot.send(error_reply(WAVES_CODE_103))
        im = await draw_char_detail_img(ev, uid, char, user_id, waves_id)
        at_sender = False
        if isinstance(im, str):
            return await bot.send(im, at_sender)
        return await bot.send(im)


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

    im = await draw_char_score_img(ev, uid, char, user_id, waves_id)
    at_sender = False
    if isinstance(im, str) and ev.group_id:
        at_sender = True
    return await bot.send(im, at_sender)
