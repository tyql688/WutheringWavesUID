import time
from pathlib import Path
from typing import List

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.api.model import AccountBaseInfo, RoleDetailData
from ..utils.button import WavesButton
from ..utils.cache import TimedCache
from ..utils.char_info_utils import get_all_role_detail_info_list
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_102
from ..utils.expression_ctx import WavesCharRank, get_waves_char_rank
from ..utils.fonts.waves_fonts import (
    waves_font_25,
    waves_font_26,
    waves_font_30,
    waves_font_40,
    waves_font_42,
    waves_font_60,
)
from ..utils.hint import error_reply
from ..utils.image import (
    CHAIN_COLOR,
    GOLD,
    GREY,
    RED,
    add_footer,
    draw_text_with_shadow,
    get_event_avatar,
    get_random_share_bg_path,
    get_square_avatar,
)
from ..utils.refresh_char_detail import refresh_char
from ..utils.resource.constant import NAME_ALIAS, SPECIAL_CHAR_NAME
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import PREFIX, WutheringWavesConfig

TEXT_PATH = Path(__file__).parent / "texture2d"

refresh_char_bg = Image.open(TEXT_PATH / "refresh_char_bg.png")
refresh_yes = Image.open(TEXT_PATH / "refresh_yes.png")
refresh_yes = refresh_yes.resize((40, 40))
refresh_no = Image.open(TEXT_PATH / "refresh_no.png")
refresh_no = refresh_no.resize((40, 40))


refresh_role_map = {
    "share_02.webp": (1000, 180, 2560, 1320),
    "share_14.webp": (1000, 180, 2560, 1320),
}

refresh_interval: int = WutheringWavesConfig.get_config("RefreshInterval").data

if refresh_interval > 0:
    timed_cache = TimedCache(timeout=refresh_interval, maxsize=10000)
else:
    timed_cache = None


def can_refresh_card(user_id: str, uid: str) -> int:
    """检查是否可以刷新角色面板"""
    key = f"{user_id}_{uid}"
    if timed_cache:
        now = int(time.time())
        time_stamp = timed_cache.get(key)
        if time_stamp and time_stamp > now:
            return time_stamp - now
    return 0


def set_cache_refresh_card(user_id: str, uid: str):
    """设置缓存"""
    if timed_cache:
        key = f"{user_id}_{uid}"
        timed_cache.set(key, int(time.time()) + refresh_interval)


def get_refresh_interval_notify(time_stamp: int):
    try:
        value: str = WutheringWavesConfig.get_config("RefreshIntervalNotify").data
        return value.format(time_stamp)
    except Exception:
        return "请等待{0}s后尝试刷新面板！".format(time_stamp)


async def get_refresh_role_img(width: int, height: int):
    path = await get_random_share_bg_path()
    img = Image.open(path).convert("RGBA")
    if path.name in refresh_role_map:
        img = img.crop(refresh_role_map[path.name])
    else:
        # 2560, 1440
        img = img.crop((700, 100, 2300, 1340))
    if height > img.height:
        img = crop_center_img(img, width, height)
    else:
        img = img.resize((width, int(width / img.width * img.height)))
    img = img.filter(ImageFilter.GaussianBlur(radius=10))
    img = ImageEnhance.Brightness(img).enhance(0.7)
    return img


async def draw_refresh_char_detail_img(
    bot: Bot,
    ev: Event,
    user_id: str,
    uid: str,
    buttons: List[WavesButton],
):
    time_stamp = can_refresh_card(user_id, uid)
    if time_stamp > 0:
        return get_refresh_interval_notify(time_stamp)
    self_ck, ck = await waves_api.get_ck_result(uid, user_id)
    if not ck:
        return error_reply(WAVES_CODE_102)
    # 账户数据
    succ, account_info = await waves_api.get_base_info(uid, ck)
    if not succ:
        return account_info
    account_info = AccountBaseInfo.model_validate(account_info)
    # 更新group id
    await WavesBind.insert_waves_uid(
        user_id, ev.bot_id, uid, ev.group_id, lenth_limit=9
    )

    waves_map = {"refresh_update": {}, "refresh_unchanged": {}}
    if ev.command == "面板":
        all_waves_datas = await get_all_role_detail_info_list(uid)
        if not all_waves_datas:
            return "暂无面板数据"
        waves_map = {
            "refresh_update": {},
            "refresh_unchanged": {
                i.role.roleId: i.model_dump() for i in all_waves_datas
            },
        }
    else:
        waves_datas = await refresh_char(
            uid, user_id, ck, waves_map=waves_map, is_self_ck=self_ck
        )
        if isinstance(waves_datas, str):
            return waves_datas

    role_detail_list = [
        RoleDetailData(**r)
        for key in ["refresh_update", "refresh_unchanged"]
        for r in waves_map[key].values()
    ]

    # 总角色个数
    role_len = len(role_detail_list)
    # 刷新个数
    role_update = len(waves_map["refresh_update"])
    shadow_title = "刷新成功!"
    shadow_color = GOLD
    if role_update == 0:
        shadow_title = "数据未更新"
        shadow_color = RED

    role_high = role_len // 6 + (0 if role_len % 6 == 0 else 1)
    height = 470 + 50 + role_high * 330
    width = 2000
    # img = get_waves_bg(width, height, "bg3")
    img = Image.new("RGBA", (width, height))
    img.alpha_composite(await get_refresh_role_img(width, height), (0, 0))

    # 提示文案
    title = f"共刷新{role_update}个角色，可以使用"
    name = role_detail_list[0].role.roleName
    name = NAME_ALIAS.get(name, name)
    title2 = f"{PREFIX}{name}面板"
    title3 = "来查询该角色的具体面板"
    info_block = Image.new("RGBA", (980, 50), color=(255, 255, 255, 0))
    info_block_draw = ImageDraw.Draw(info_block)
    info_block_draw.rounded_rectangle(
        [0, 0, 980, 50], radius=15, fill=(128, 128, 128, int(0.3 * 255))
    )
    info_block_draw.text((50, 24), f"{title}", GREY, waves_font_30, "lm")
    info_block_draw.text(
        (50 + len(title) * 28 + 20, 24), f"{title2}", (255, 180, 0), waves_font_30, "lm"
    )
    info_block_draw.text(
        (50 + len(title) * 28 + 20 + len(title2) * 28 + 10, 24),
        f"{title3}",
        GREY,
        waves_font_30,
        "lm",
    )
    img.alpha_composite(info_block, (500, 400))

    waves_char_rank = await get_waves_char_rank(uid, role_detail_list)

    map_update = []
    map_unchanged = []
    for _, char_rank in enumerate(waves_char_rank):
        isUpdate = True if char_rank.roleId in waves_map["refresh_update"] else False
        if isUpdate:
            map_update.append(char_rank)
        else:
            map_unchanged.append(char_rank)

    map_update.sort(key=lambda x: x.score if x.score else 0, reverse=True)
    map_unchanged.sort(key=lambda x: x.score if x.score else 0, reverse=True)

    rIndex = 0
    for char_rank in map_update:
        pic = await draw_pic(char_rank, True)  # type: ignore
        img.alpha_composite(pic, (80 + 300 * (rIndex % 6), 470 + (rIndex // 6) * 330))
        rIndex += 1
        if rIndex <= 5:
            name = SPECIAL_CHAR_NAME.get(str(char_rank.roleId), char_rank.roleName)
            b = WavesButton(name, f"{name}面板")  # type: ignore
            buttons.append(b)

    for char_rank in map_unchanged:
        pic = await draw_pic(char_rank, False)  # type: ignore
        img.alpha_composite(pic, (80 + 300 * (rIndex % 6), 470 + (rIndex // 6) * 330))
        rIndex += 1

        if len(map_update) == 0 and rIndex <= 5:
            name = SPECIAL_CHAR_NAME.get(str(char_rank.roleId), char_rank.roleName)
            b = WavesButton(name, f"{name}面板")  # type: ignore
            buttons.append(b)

    buttons.append(WavesButton("练度统计", "练度统计"))

    # 基础信息 名字 特征码
    base_info_bg = Image.open(TEXT_PATH / "base_info_bg.png")
    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text(
        (275, 120), f"{account_info.name[:7]}", "white", waves_font_30, "lm"
    )
    base_info_draw.text(
        (226, 173), f"特征码:  {account_info.id}", GOLD, waves_font_25, "lm"
    )
    img.paste(base_info_bg, (15, 20), base_info_bg)

    # 头像 头像环
    avatar = await draw_pic_with_ring(ev)
    avatar_ring = Image.open(TEXT_PATH / "avatar_ring.png")
    img.paste(avatar, (25, 70), avatar)
    avatar_ring = avatar_ring.resize((180, 180))
    img.paste(avatar_ring, (35, 80), avatar_ring)

    # 账号基本信息，由于可能会没有，放在一起
    if account_info.is_full:
        title_bar = Image.open(TEXT_PATH / "title_bar.png")
        title_bar_draw = ImageDraw.Draw(title_bar)
        title_bar_draw.text((660, 125), "账号等级", GREY, waves_font_26, "mm")
        title_bar_draw.text(
            (660, 78), f"Lv.{account_info.level}", "white", waves_font_42, "mm"
        )

        title_bar_draw.text((810, 125), "世界等级", GREY, waves_font_26, "mm")
        title_bar_draw.text(
            (810, 78), f"Lv.{account_info.worldLevel}", "white", waves_font_42, "mm"
        )
        img.paste(title_bar, (-20, 70), title_bar)

    # bar
    refresh_bar = Image.open(TEXT_PATH / "refresh_bar.png")
    refresh_bar_draw = ImageDraw.Draw(refresh_bar)
    draw_text_with_shadow(
        refresh_bar_draw,
        f"{shadow_title}",
        1010,
        40,
        waves_font_60,
        shadow_color=shadow_color,
        offset=(2, 2),
        anchor="mm",
    )
    draw_text_with_shadow(
        refresh_bar_draw,
        "登录状态:",
        1700,
        20,
        waves_font_40,
        shadow_color=GOLD,
        offset=(2, 2),
        anchor="mm",
    )
    if self_ck:
        refresh_bar.alpha_composite(refresh_yes.resize((60, 60)), (1800, -8))
    else:
        refresh_bar.alpha_composite(refresh_no.resize((60, 60)), (1800, -8))

    img.paste(refresh_bar, (0, 300), refresh_bar)
    img = add_footer(img)
    img = await convert_img(img)
    set_cache_refresh_card(user_id, uid)
    return img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img


async def draw_pic(char_rank: WavesCharRank, isUpdate=False):
    pic = await get_square_avatar(char_rank.roleId)
    resize_pic = pic.resize((200, 200))
    img = refresh_char_bg.copy()
    img_draw = ImageDraw.Draw(img)
    img.alpha_composite(resize_pic, (50, 50))
    # 名字
    roleName = SPECIAL_CHAR_NAME.get(str(char_rank.roleId), char_rank.roleName)

    img_draw.text((150, 290), f"{roleName}", "white", waves_font_40, "mm")
    # 命座
    info_block = Image.new("RGBA", (80, 40), color=(255, 255, 255, 0))
    info_block_draw = ImageDraw.Draw(info_block)
    fill = CHAIN_COLOR[char_rank.chain] + (int(0.9 * 255),)
    info_block_draw.rounded_rectangle([0, 0, 80, 40], radius=5, fill=fill)
    info_block_draw.text(
        (12, 20), f"{char_rank.chainName}", "white", waves_font_30, "lm"
    )
    img.alpha_composite(info_block, (200, 15))

    # 评分
    if char_rank.score > 0.0:
        name_len = len(roleName)
        _x = 150 + int(43 * (name_len / 2))
        score_bg = Image.open(TEXT_PATH / f"refresh_{char_rank.score_bg}.png")
        img.alpha_composite(score_bg, (_x, 265))

    if isUpdate:
        name_len = len(roleName)
        _x = 100 - int(43 * (name_len / 2))
        img.alpha_composite(refresh_yes, (_x, 270))

    return img
