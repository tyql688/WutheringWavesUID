from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img
from gsuid_core.utils.image.utils import sget
from ..utils.api.model import KuroRoleInfo, AccountBaseInfo, RoleList, ChallengeArea
from ..utils.error_reply import WAVES_CODE_102
from ..utils.fonts.waves_fonts import waves_font_26, waves_font_42, waves_font_30, waves_font_25, waves_font_18, \
    waves_font_24
from ..utils.hint import error_reply
from ..utils.image import get_waves_bg, GREY, get_event_avatar, get_square_avatar, add_footer, GOLD
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / 'texture2d'


async def draw_challenge_img(
    ev: Event,
    uid: str,
) -> Union[bytes, str]:
    is_self_ck, ck = await waves_api.get_ck_result(uid)
    if not ck:
        return error_reply(WAVES_CODE_102)

    succ, game_info = await waves_api.get_game_role_info(ck)
    if not succ:
        return game_info
    game_info = KuroRoleInfo(**game_info)

    # 全息数据
    succ, challenge_data = await waves_api.get_challenge_data(uid, ck)
    if not succ:
        return challenge_data
    challenge_data = ChallengeArea(**challenge_data)
    if not challenge_data.open:
        return '您未打开库街区[全息挑战]的对外展示'

    # 账户数据
    succ, account_info = await waves_api.get_base_info(uid, ck)
    account_info = AccountBaseInfo(**account_info)

    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(uid, ck)
    if not succ:
        return role_info
    role_info = RoleList(**role_info)

    h = 350 + len(challenge_data.challengeInfo) * 330 + 30
    card_img = get_waves_bg(950, h, 'bg3')

    # 基础信息 名字 特征码
    base_info_bg = Image.open(TEXT_PATH / 'base_info_bg.png')
    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text((275, 120), f'{account_info.name[:7]}', 'white', waves_font_30, 'lm')
    base_info_draw.text((226, 173), f'特征码:  {account_info.id}', GOLD, waves_font_25, 'lm')
    card_img.paste(base_info_bg, (15, 20), base_info_bg)

    # 头像 头像环
    avatar = await draw_pic_with_ring(ev)
    avatar_ring = Image.open(TEXT_PATH / 'avatar_ring.png')
    card_img.paste(avatar, (25, 70), avatar)
    avatar_ring = avatar_ring.resize((180, 180))
    card_img.paste(avatar_ring, (35, 80), avatar_ring)

    # 账号基本信息，由于可能会没有，放在一起
    if account_info.is_full:
        title_bar = Image.open(TEXT_PATH / 'title_bar.png')
        title_bar_draw = ImageDraw.Draw(title_bar)
        title_bar_draw.text((660, 125), '账号等级', GREY, waves_font_26, 'mm')
        title_bar_draw.text((660, 78), f'Lv.{account_info.level}', 'white', waves_font_42, 'mm')

        title_bar_draw.text((810, 125), '世界等级', GREY, waves_font_26, 'mm')
        title_bar_draw.text((810, 78), f'Lv.{account_info.worldLevel}', 'white', waves_font_42, 'mm')
        card_img.paste(title_bar, (-20, 70), title_bar)

    challenge_index = 0
    for challenge_id, _challenge in challenge_data.challengeInfo.items():
        max_num = len(_challenge)
        boss_title_bg = Image.new("RGBA", (1000, 100))
        boss_title_bg_draw = ImageDraw.Draw(boss_title_bg)
        boss_difficulty = 1
        boss_level = 1
        boss_icon_bg = Image.open(BytesIO((await sget(_challenge[0].bossIconUrl)).content)).convert('RGBA')
        boss_icon_bg = boss_icon_bg.resize((800, 212))
        for _temp in reversed(_challenge):
            boss_difficulty = _temp.difficulty
            boss_level = _temp.bossLevel
            if not _temp.roles:
                continue
            boss_title_bg_draw.text((600, 20), f'通关时间：{timedelta(seconds=_temp.passTime)}', 'white', waves_font_24,
                                    'lm')

            for role_index, _role in enumerate(_temp.roles):
                role = next((role for role in role_info.roleList if
                             role.roleName == _role.roleName or _role.roleName in role.roleName), None)
                if not role:
                    logger.error(f'角色[{_role.roleName}]未找到')
                avatar = await draw_pic(role.roleId)
                char_bg = Image.open(TEXT_PATH / f'char_bg{role.starLevel}.png')
                char_bg_draw = ImageDraw.Draw(char_bg)
                char_bg_draw.text((90, 150), f'{role.roleName}', 'white', waves_font_18, 'mm')
                char_bg.paste(avatar, (0, 0), avatar)

                info_block = Image.new("RGBA", (40, 20), color=(255, 255, 255, 0))
                info_block_draw = ImageDraw.Draw(info_block)
                info_block_draw.rectangle([0, 0, 40, 20], fill=(96, 12, 120, int(0.9 * 255)))
                info_block_draw.text((2, 10), f'{_role.roleLevel}', 'white', waves_font_18, 'lm')
                char_bg.paste(info_block, (110, 35), info_block)

                boss_icon_bg.alpha_composite(char_bg, (350 + role_index * 150, 30))

            break
        card_img.alpha_composite(boss_icon_bg, (80, 350 + challenge_index * 330))
        boss_title_bg_draw.text((100, 50), f'{_challenge[0].bossName}', 'white', waves_font_42, 'lm')
        boss_title_bg_draw.text((300, 60), f'Lv.{boss_level}', 'white', waves_font_24, 'lm')
        boss_title_bg_draw.text((600, 60), f'当前难度：{boss_difficulty}/{max_num}', 'white', waves_font_24, 'lm')

        card_img.paste(boss_title_bg, (-20, 260 + 330 * challenge_index), boss_title_bg)
        challenge_index += 1

    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev)

    mask_pic = Image.open(TEXT_PATH / 'avatar_mask.png')
    img = Image.new('RGBA', (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img


async def draw_pic(roleId):
    pic = await get_square_avatar(roleId)
    mask_pic = Image.open(TEXT_PATH / 'avatar_mask.png')
    img = Image.new('RGBA', (180, 180))
    mask = mask_pic.resize((140, 140))
    resize_pic = crop_center_img(pic, 140, 140)
    img.paste(resize_pic, (22, 18), mask)

    return img
