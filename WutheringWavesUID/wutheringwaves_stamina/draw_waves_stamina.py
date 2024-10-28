import asyncio
import time
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img
from ..utils.api.model import DailyData
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103, ERROR_CODE, WAVES_CODE_102
from ..utils.fonts.waves_fonts import waves_font_30, waves_font_25, waves_font_24
from ..utils.image import add_footer, GREY, GOLD, get_random_waves_role_pile, YELLOW, get_event_avatar, RED
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / 'texture2d'
YES = Image.open(TEXT_PATH / 'yes.png')
YES = YES.resize((40, 40))
NO = Image.open(TEXT_PATH / 'no.png')
NO = NO.resize((40, 40))

based_w = 1150
based_h = 650


async def seconds2hours(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return '%02d小时%02d分' % (h, m)


async def draw_stamina_img(bot: Bot, ev: Event):
    try:
        uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
        logger.info(f'[鸣潮][每日信息]UID: {uid_list}')
        if uid_list is None:
            return ERROR_CODE[WAVES_CODE_103]
        # 进行校验UID是否绑定CK
        valid_daily_list = []
        for uid in uid_list:
            ck = await waves_api.get_self_waves_ck(uid)
            if not ck:
                continue
            succ, _ = await waves_api.refresh_data(uid, ck)
            if not succ:
                continue
            succ, daily_info = await waves_api.get_daily_info(ck)
            if not succ:
                continue
            daily_info = DailyData(**daily_info)
            valid_daily_list.append(daily_info)

        if len(valid_daily_list) == 0:
            return ERROR_CODE[WAVES_CODE_102]

        # 开始绘图任务
        task = []
        img = Image.new(
            'RGBA', (based_w, based_h * len(valid_daily_list)), (0, 0, 0, 0)
        )
        for uid_index, temp in enumerate(valid_daily_list):
            task.append(_draw_all_stamina_img(ev, img, temp, uid_index))
        await asyncio.gather(*task)
        res = await convert_img(img)
        logger.info('[鸣潮][每日信息]绘图已完成,等待发送!')
    except TypeError:
        logger.exception('[鸣潮][每日信息]绘图失败!')
        res = '你绑定过的UID中可能存在过期CK~请重新绑定一下噢~'

    return res


async def _draw_all_stamina_img(ev: Event, img: Image.Image, daily_info: DailyData, index: int):
    stamina_img = await _draw_stamina_img(ev, daily_info)
    stamina_img = stamina_img.convert('RGBA')
    img.paste(stamina_img, (0, based_h * index), stamina_img)


async def _draw_stamina_img(ev: Event, daily_info: DailyData) -> Union[str, Image.Image]:
    if daily_info.hasSignIn:
        sign_in_icon = YES
        sing_in_text = '签到已完成！'
    else:
        sign_in_icon = NO
        sing_in_text = '今日未签到！'

    if daily_info.livenessData.total != 0 and daily_info.livenessData.cur == daily_info.livenessData.total:
        active_icon = YES
        active_text = '活跃度已满！'
    else:
        active_icon = NO
        active_text = '活跃度未满！'

    img = Image.open(TEXT_PATH / 'bg_new.jpg').convert("RGBA")
    info = Image.open(TEXT_PATH / 'info_new.png').convert("RGBA")
    base_info_bg = Image.open(TEXT_PATH / 'base_info_bg.png')
    avatar_ring = Image.open(TEXT_PATH / 'avatar_ring.png')

    # 头像
    avatar = await draw_pic_with_ring(ev)

    # 随机获得pile
    pile = await get_random_waves_role_pile()
    pile = pile.crop((0, 0, pile.size[0], pile.size[1] - 155))

    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text((275, 120), f'{daily_info.roleName[:7]}', GREY, waves_font_30, 'lm')
    base_info_draw.text((226, 173), f'特征码:  {daily_info.roleId}', GOLD, waves_font_25, 'lm')

    # 体力剩余恢复时间
    curr_time = int(time.time())
    refreshTimeStamp = daily_info.energyData.refreshTimeStamp if daily_info.energyData.refreshTimeStamp else curr_time
    remain_time = await seconds2hours(refreshTimeStamp - curr_time)
    active_draw = ImageDraw.Draw(info)
    active_draw.text((178, 140), f'剩余时间', GREY, waves_font_24, 'lm')

    time_img = Image.new('RGBA', (155, 30), (255, 255, 255, 0))
    time_img_draw = ImageDraw.Draw(time_img)
    time_img_draw.rounded_rectangle([0, 0, 155, 30], radius=15, fill=(186, 55, 42, int(0.7 * 255)))
    time_img_draw.text((10, 15), f'{remain_time}', 'white', waves_font_24, 'lm')
    info.alpha_composite(time_img, (280, 125))

    max_len = 345
    # 体力
    active_draw.text((350, 184), f'/{daily_info.energyData.total}', GREY, waves_font_30, 'lm')
    active_draw.text((348, 184), f'{daily_info.energyData.cur}', GREY, waves_font_30, 'rm')
    radio = daily_info.energyData.cur / daily_info.energyData.total
    color = RED if radio > 0.8 else YELLOW
    active_draw.rectangle((173, 216, int(173 + radio * max_len), 224), color)
    # 活跃度
    active_draw.text((350, 300), f'/{daily_info.livenessData.total}', GREY, waves_font_30, 'lm')
    active_draw.text((348, 300), f'{daily_info.livenessData.cur}', GREY, waves_font_30, 'rm')
    radio = daily_info.livenessData.cur / daily_info.livenessData.total if daily_info.livenessData.total != 0 else 0
    active_draw.rectangle((173, 325, int(173 + radio * max_len), 333), YELLOW)

    # 签到状态
    status_img = Image.new('RGBA', (230, 40), (255, 255, 255, 0))
    status_img_draw = ImageDraw.Draw(status_img)
    status_img_draw.rounded_rectangle([0, 0, 230, 40], fill=(0, 0, 0, int(0.3 * 255)))
    status_img.alpha_composite(sign_in_icon, (0, 0))
    status_img_draw.text((50, 20), f'{sing_in_text}', 'white', waves_font_30, 'lm')
    img.alpha_composite(status_img, (70, 220))

    # 活跃状态
    status_img2 = Image.new('RGBA', (230, 40), (255, 255, 255, 0))
    status_img2_draw = ImageDraw.Draw(status_img2)
    status_img2_draw.rounded_rectangle([0, 0, 230, 40], fill=(0, 0, 0, int(0.3 * 255)))
    status_img2.alpha_composite(active_icon, (0, 0))
    status_img2_draw.text((50, 20), f'{active_text}', 'white', waves_font_30, 'lm')
    img.alpha_composite(status_img2, (320, 220))

    # pile 放在背景上
    img.paste(pile, (550, -200), pile)
    # info 放在背景上
    img.paste(info, (20, 190), info)
    # base_info 放在背景上
    img.paste(base_info_bg, (40, -10), base_info_bg)
    # avatar_ring 放在背景上
    img.paste(avatar_ring, (40, 40), avatar_ring)
    img.paste(avatar, (40, 40), avatar)
    img = add_footer(img, 600, 20)
    return img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev, is_valid_at=False)

    mask_pic = Image.open(TEXT_PATH / 'avatar_mask.png')
    img = Image.new('RGBA', (200, 200))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img
