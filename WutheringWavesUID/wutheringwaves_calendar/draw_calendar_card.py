import random
from datetime import timedelta, datetime
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img
from gsuid_core.utils.image.utils import sget
from .calendar_model import SpecialImages, VersionActivity
from ..utils.api.requests import Wiki
from ..utils.ascension.char import get_char_id
from ..utils.ascension.weapon import get_weapon_id
from ..utils.fonts.waves_fonts import waves_font_20, waves_font_30, waves_font_24
from ..utils.image import get_square_avatar, get_square_weapon, add_footer, SPECIAL_GOLD

TEXT_PATH = Path(__file__).parent / 'texture2d'
time_icon = Image.open(TEXT_PATH / 'time_icon.png')
wiki = Wiki()


def tower_node(now: datetime):
    start_time = datetime(2024, 11, 25, 4, 0)
    date_range = 86400 * 14  # 14天为一周期（秒）
    # 将秒数转为 timedelta 对象
    date_range_td = timedelta(seconds=date_range)

    # 计算周期编号
    elapsed_time = (now - start_time).total_seconds()  # 当前时间与开始时间的差值（秒）
    period_index = int(elapsed_time // date_range)  # 周期编号（从 0 开始）

    # 当前周期的起始和结束时间
    period_start = start_time + period_index * date_range_td
    period_end = period_start + date_range_td

    start_date_str = period_start.strftime("%Y-%m-%d %H:%M")
    end_date_str = period_end.strftime("%Y-%m-%d %H:%M")

    return {
        "title": "逆境深塔",
        "contentUrl": "tower.png",
        "countDown": {
            "dateRange": [start_date_str, end_date_str]
        }
    }


async def draw_calendar_img(ev: Event, uid: str):
    wiki_home = await wiki.get_wiki_home()
    if wiki_home['code'] != 200:
        return

    # 当前时间
    now = datetime.now()

    gacha_char_list = []
    gacha_weapon_list = []
    content = None
    side_modules = wiki_home.get("data", {}).get("contentJson", {}).get("sideModules", [])
    for side_module in side_modules:
        if side_module['title'] == '角色唤取活动':
            gacha_char_list = await draw_calendar_gacha(side_module, '角色')
            logger.info(f'{gacha_char_list}')

        elif side_module['title'] == '武器活动唤取':
            gacha_weapon_list = await draw_calendar_gacha(side_module, '武器')

            logger.info(f'{gacha_weapon_list}')

        elif side_module['title'] == '版本活动':
            side_module['content'].insert(0, tower_node(now))
            content = VersionActivity(**side_module)

    title_high = 150
    banner_high = 550
    bar1_high = 60
    char_bar_high = 150
    star_fg_high = 150
    weapon_bar_high = 150
    bar2_high = 60
    event_high = 170
    temp_high = 20
    footer_high = 70

    content_total_row = 1 + (len(content.content) - 1) // 2
    total_high = title_high + banner_high + temp_high + content_total_row * event_high + bar2_high + footer_high
    if gacha_char_list:
        total_high += (char_bar_high + star_fg_high * len(gacha_char_list)) * 2
        total_high += temp_high
        total_high += bar1_high

    bg = f"bg{random.choice([1, 2])}"
    img = await get_calendar_bg(1200, total_high, bg)
    # title
    title_img = Image.open(TEXT_PATH / 'title.png')

    img.paste(title_img, (0, 50), title_img)

    # banner
    await draw_banner(wiki_home, img)

    _high = title_high + banner_high
    # 卡池title
    if gacha_char_list:
        bar1 = Image.open(TEXT_PATH / 'bar1.png')
        img.paste(bar1, (0, _high), bar1)
        _high = _high + bar1_high
        char_bar = Image.open(TEXT_PATH / 'char_bar.png')

        if gacha_char_list[0]['dateRange']:
            char_bar_draw = ImageDraw.Draw(char_bar)
            dateRange = gacha_char_list[0]['dateRange']
            status, left, color = get_date_range(dateRange, now)
            if left:
                status = f"{status}: "
                char_bar_draw.text((310, 110), f'{left}', color, waves_font_24, 'lm')
            char_bar_draw.text((220, 110), f'{status}', 'white', waves_font_24, 'lm')

        img.paste(char_bar, (0, _high), char_bar)
        _high += char_bar_high
        _high = draw_gacha(gacha_char_list, img, _high)

    if gacha_weapon_list:
        _high += temp_high
        weapon_bar = Image.open(TEXT_PATH / 'weapon_bar.png')
        if gacha_char_list[0]['dateRange']:
            weapon_bar_draw = ImageDraw.Draw(weapon_bar)
            dateRange = gacha_char_list[0]['dateRange']
            status, left, color = get_date_range(dateRange, now)
            if left:
                status = f"{status}: "
                weapon_bar_draw.text((310, 110), f'{left}', color, waves_font_24, 'lm')
            weapon_bar_draw.text((220, 110), f'{status}', 'white', waves_font_24, 'lm')

        img.paste(weapon_bar, (0, _high), weapon_bar)
        _high += weapon_bar_high
        _high = draw_gacha(gacha_weapon_list, img, _high)

    # 活动bar
    _high += temp_high
    bar2 = Image.open(TEXT_PATH / 'bar2.png')

    img.paste(bar2, (0, _high), bar2)
    _high += bar2_high
    for i, cont in enumerate(content.content):
        event_bg = Image.open(TEXT_PATH / 'event_bg.png')
        event_bg_draw = ImageDraw.Draw(event_bg)
        dateRange = []
        if cont.countDown:
            dateRange = cont.countDown.dateRange

        if dateRange:
            start_time = datetime.strptime(dateRange[0], '%Y-%m-%d %H:%M')
            end_time = datetime.strptime(dateRange[1], '%Y-%m-%d %H:%M')

            status, left, color = get_date_range(dateRange, now)
            if left:
                event_bg_draw.text((260, 130), f'{left}', color, waves_font_20, 'lm')
                status = f"{status}: "

            # 格式化
            formatted_start = start_time.strftime('%m.%d %H:%M')
            formatted_end = end_time.strftime('%m.%d %H:%M')

            # 起止时间
            formatted_date_range = f"{formatted_start} ~ {formatted_end}"
            event_bg_draw.text((160, 95), f'{formatted_date_range}', 'white', waves_font_20, 'lm')
            # 时间小图标
            event_bg.alpha_composite(time_icon, (155, 115))
            # 状态
            event_bg_draw.text((190, 130), f'{status}', 'white', waves_font_20, 'lm')

        if 'http' in cont.contentUrl:
            linkUrl = Image.open(BytesIO((await sget(cont.contentUrl)).content)).convert(
                'RGBA'
            )
        else:
            linkUrl = Image.open(TEXT_PATH / cont.contentUrl)
        linkUrl = linkUrl.resize((100, 100))
        event_bg.paste(linkUrl, (40, 40), linkUrl)
        event_bg_draw.text((160, 60), f'{cont.title}', SPECIAL_GOLD, waves_font_30, 'lm')

        img.alpha_composite(event_bg, (70 + (i % 2) * 540, _high))
        if i % 2 == 1:
            _high += event_high

    img = add_footer(img)
    img = await convert_img(img)
    return img


async def draw_calendar_gacha(side_module, gacha_type):
    res_list = []
    tabs = side_module['content']['tabs']
    for tab in tabs:
        if 'description' not in tab or not tab.get('description', ''):
            continue
        special_images = SpecialImages(**tab)
        res = {
            'title': side_module['title'],
            'dateRange': tab['countDown']['dateRange'],
            'description': tab['description'],
            'nodes': []
        }
        for img_item in special_images.imgs:
            item_detail = await wiki.get_entry_detail(img_item.linkConfig.entryId)
            if item_detail['code'] == 200:
                name = item_detail['data']['name']
                if gacha_type == "角色":
                    id = get_char_id(name)
                    pic = await get_square_avatar(id)
                    pic = pic.resize((180, 180))
                else:
                    id = get_weapon_id(name)
                    pic = await get_square_weapon(id)
                res['nodes'].append({
                    'name': name,
                    'id': id,
                    'pic': pic
                })
        res_list.append(res)

    return res_list


async def draw_banner(wiki_home, img):
    banners = wiki_home.get("data", {}).get("contentJson", {}).get("banner", [])
    banner_bg = banners[0]['url']
    for banner in banners:
        if '版本' in banner['describe']:
            banner_bg = banner['url']
            break

    logger.info(f'banner_bg: {banner_bg}')

    banner_bg = Image.open(BytesIO((await sget(banner_bg)).content)).convert(
        'RGBA'
    )

    banner_bg = banner_bg.resize((1200, 675))
    banner_mask = Image.open(TEXT_PATH / 'banner_mask.png')
    banner_bg = crop_center_img(banner_bg, banner_mask.size[0], banner_mask.size[1])

    banner_bg_temp = Image.new('RGBA', banner_mask.size, (255, 255, 255, 0))
    banner_bg_temp.paste(banner_bg, (0, 0), banner_mask)
    banner_frame_img = Image.open(TEXT_PATH / 'banner_frame.png')

    img.paste(banner_bg, (0, 150), banner_mask)
    img.paste(banner_frame_img, (0, 150), banner_frame_img)


async def get_calendar_bg(w: int, h: int, bg: str = 'bg1') -> Image.Image:
    img = Image.open(TEXT_PATH / f'{bg}.jpg').convert('RGBA')
    return crop_center_img(img, w, h)


def draw_gacha(gacha_list, img, _high):
    star_fg_high = 150
    for i, gacha_list in enumerate(gacha_list):
        gacha_bg = Image.new('RGBA', (1200, star_fg_high), (0, 0, 0, 0))
        for j, gacha in enumerate(gacha_list['nodes']):
            if j == 0:
                star_fg = Image.open(TEXT_PATH / 'star5_fg.png')
                star_bg = Image.open(TEXT_PATH / 'star5_bg.png')
            else:
                star_fg = Image.open(TEXT_PATH / 'star4_fg.png')
                star_bg = Image.open(TEXT_PATH / 'star4_bg.png')

            star_bg_temp = Image.new('RGBA', star_bg.size)
            star_bg_temp.paste(star_bg, (0, 0))
            star_bg_temp.alpha_composite(gacha['pic'], (80, -10))

            gacha_name = gacha["name"]
            if len(gacha_name) <= 2:
                name_bg = Image.new("RGBA", (60, 25), color=(255, 255, 255, 0))
                rank_draw = ImageDraw.Draw(name_bg)
                rank_draw.rectangle([0, 0, 60, 25], fill=(255, 255, 255) + (int(0.9 * 255),))
                rank_draw.text((30, 12), f'{gacha_name}', 'black', waves_font_20, 'mm')
            else:
                name_bg = Image.new("RGBA", (80, 25), color=(255, 255, 255, 0))
                rank_draw = ImageDraw.Draw(name_bg)
                rank_draw.rectangle([0, 0, 80, 25], fill=(255, 255, 255) + (int(0.9 * 255),))
                rank_draw.text((40, 12), f'{gacha_name}', 'black', waves_font_20, 'mm')

            gacha_bg.paste(star_bg_temp, (80 + j * 260, 0))
            gacha_bg.alpha_composite(star_fg, (80 + j * 260, 0))
            gacha_bg.alpha_composite(name_bg, (90 + j * 260, 110))

        img.alpha_composite(gacha_bg, (0, _high))
        _high += star_fg_high
    return _high


def get_left_time_str(remaining_time):
    # 提取天数、小时数和分钟数
    remaining_days = remaining_time.days
    remaining_hours, remaining_minutes = divmod(remaining_time.seconds, 3600)
    remaining_minutes, remaining_seconds = divmod(remaining_minutes, 60)
    # 剩余时间
    return f"还剩{remaining_days}天{remaining_hours}小时{remaining_minutes}分钟"


def get_date_range(dateRange, now):
    start_time = datetime.strptime(dateRange[0], '%Y-%m-%d %H:%M')
    end_time = datetime.strptime(dateRange[1], '%Y-%m-%d %H:%M')
    left = ''
    color = 'white'
    if start_time <= now <= end_time:
        # 进行中
        status = '进行中'
        if end_time >= now:
            remaining_time = end_time - now
            left = get_left_time_str(remaining_time)
            if remaining_time.days <= 3:
                color = 'red'
    elif now > end_time:
        # 已结束
        status = '已结束'
    else:
        # 未开始
        status = '未开始'

    return status, left, color