import asyncio
import copy
from pathlib import Path
from typing import Dict, Union

import httpx
from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.wwapi import GET_HOLD_RATE_URL
from ..utils.ascension.char import get_char_model
from ..utils.database.models import WavesBind
from ..utils.fonts.waves_fonts import (
    waves_font_24,
    waves_font_36,
    waves_font_58,
)
from ..utils.image import (
    CHAIN_COLOR_LIST,
    GOLD,
    SPECIAL_GOLD,
    add_footer,
    get_attribute,
    get_ICON,
    get_square_avatar,
    get_waves_bg,
)
from ..utils.resource.constant import (
    ATTRIBUTE_ID_MAP,
    NORMAL_LIST_IDS,
    SPECIAL_CHAR_NAME,
)
from ..utils.util import timed_async_cache
from ..utils.waves_card_cache import get_card

TEXT_PATH = Path(__file__).parent / "texture2d"
bar1 = Image.open(TEXT_PATH / "bar1.png")
avatar_mask = Image.open(TEXT_PATH / "avatar_mask.png")


# 常驻颜色
STAR_FOUR = (219, 68, 255)
STAR_FIVE = SPECIAL_GOLD
OTHER_STAR = GOLD


async def draw_char_chain_hold_rate(ev: Event, data, group_id: str = "") -> bytes:
    text = ev.text.strip() if ev.text else ""
    if "4" in text or "四" in text:
        filter_type = "四"
    elif "5" in text or "五" in text:
        filter_type = "五"
    elif "up" in text or "UP" in text:
        filter_type = "UP"
    elif "all" in text or "ALL" in text or "全" in text:
        filter_type = ""
    else:
        filter_type = "五"  # 默认显示五星角色

    # 收集所有共鸣链数据
    chain_data_list = []
    total_items = 0
    
    # 整合到一个循环中处理数据
    for char in data["char_hold_rate"]:
        char_id = char["char_id"]
        char_model = get_char_model(char_id)
        if not char_model:
            continue
            
        # 应用过滤器
        if filter_type:
            if filter_type == "UP":
                if not (
                    char_model.starLevel == 5
                    and int(char_id) not in NORMAL_LIST_IDS
                    and str(char_id) not in SPECIAL_CHAR_NAME
                ):
                    continue
            elif filter_type == "五":
                if char_model.starLevel != 5:
                    continue
            elif filter_type == "四":
                if char_model.starLevel != 4:
                    continue

        use_rate = False
        hold_rate = char["hold_rate"]
        player_count = char.get("player_count", -1)
        if player_count == -1:
            use_rate = True
        chain_rates = char["chain_hold_rate"]
        
        # 计算每个共鸣链的持有数量或所占比例
        for chain_level, rate in chain_rates.items():
            num = (hold_rate * rate / 100) if use_rate else int(player_count * rate / 100)
            if num > 0:  # 只添加有持有者的链
                chain_data_list.append({
                    "char_id": char_id,
                    "char_model": char_model,
                    "chain_level": chain_level,
                    "num": num,
                    "rate": rate
                })
                total_items += 1
    
    # 按持有数量降序排序
    chain_data_list.sort(key=lambda x: x["num"], reverse=True)

    # 设置图像尺寸
    width = 1300
    margin = 30
    item_height = 130  # 每个条目的高度
    header_height = 700
    footer_height = 50
    
    # 计算最佳列数 - 基于黄金分割比 (0.618)
    # 目标宽高比 = 宽度 / 高度 ≈ 0.618
    # 因此目标高度 = 宽度 / 0.618 ≈ 2100
    target_height = width / 0.618
    
    # 计算可用高度 (减去页眉页脚和边距)
    available_height = target_height - header_height - footer_height - 2 * margin
    if available_height < 0:
        available_height = target_height  # 防止负数
    
    # 计算每列最大行数
    max_rows_per_col = max(1, int(available_height / item_height))
    
    # 计算最佳列数
    columns = max(1, min(5, (total_items + max_rows_per_col - 1) // max_rows_per_col))
    
    # 计算每列实际行数
    rows_per_column = (total_items + columns - 1) // columns
    
    # 计算总高度
    total_height = int(
        header_height 
        + rows_per_column * item_height 
        + margin * 2 
        + footer_height
    )
    
    # 创建带背景的画布 - 使用bg9
    img = get_waves_bg(width, total_height, "bg9")
    
    # title_bg
    title_bg = Image.open(TEXT_PATH / "title2.png")
    title_mask = Image.open(TEXT_PATH / "title1.png")
    title_mask_draw = ImageDraw.Draw(title_mask)
    
    # icon
    icon = get_ICON()
    icon = icon.resize((180, 180))
    title_mask.paste(icon, (60, 380), icon)
    
    # title
    title_text = f"#共鸣链持有率排行{group_id}"
    title_mask_draw.text((300, 430), title_text, "white", waves_font_58, "lm")
    
    # count
    title = (
        f"样本数量: {data.get('total_player_count', 0)} 人 | 共 {total_items} 种共鸣链"
        if group_id
        else f"样本来源：国服近期活跃角色 | 共 {total_items} 种共鸣链"
    )
    title_mask_draw.text(
        (300, 500),
        title,
        "white",
        waves_font_36,
        "lm",
    )
    
    img.paste(title_bg, (0, 0), title_bg)
    img.paste(title_mask, (0, 0), title_mask)
    
    # 绘制排行榜
    draw = ImageDraw.Draw(img)
    
    # 计算列宽 (考虑边距)
    column_width = (width - margin * (columns + 1)) // columns
    
    rank = 1
    for idx, chain_data in enumerate(chain_data_list):
        char_id = chain_data["char_id"]
        char_model = chain_data["char_model"]
        chain_level = chain_data["chain_level"]
        num = chain_data["num"]
        rate = chain_data["rate"]
        
        # 计算位置 (行和列)
        col = idx % columns
        row = idx // columns
        
        # 计算坐标
        x = margin + col * (column_width + margin)
        y = header_height + row * item_height
        
        # 绘制背景框
        bg_box = Image.new("RGBA", (column_width, item_height - 20), (0, 0, 0, 150))
        img.paste(bg_box, (x, y), bg_box)
        
        # 排名序号
        rank_text = f"{rank}."
        draw.text(
            (x + 1, y + (item_height - 20) // 2),
            rank_text,
            "white",
            waves_font_24,
            "lm"
        )
        
        # 属性图标
        attribute_text = char_model.attributeId
        attribute_name = ATTRIBUTE_ID_MAP[attribute_text]
        role_attribute = await get_attribute(attribute_name, is_simple=True)
        role_attribute = role_attribute.resize((40, 40)).convert("RGBA")
        img.alpha_composite(role_attribute, (x + 1, y + 2))

        # 角色头像
        avatar = await draw_pic(char_id)
        avatar = avatar.resize((110, 110))
        img.paste(avatar, (x + 40, y + 2), avatar)
        
        # 链级
        chain_text = f"{chain_level}链"
        draw.text(
            (x + 110, y + 20),
            chain_text,
            CHAIN_COLOR_LIST[int(chain_level)],
            waves_font_24,
            "lm"
        )
        
        # 持有数量
        num_text = f"{num:.2f}%" if use_rate else f"{num}人"
        draw.text(
            (x + 110, y + 50),
            num_text,
            "#AAAAAA",
            waves_font_24,
            "lm"
        )

        # 同角色该链持有数量占比
        num_text = f"同角占比{rate:.1f}%"
        draw.text(
            (x + 40, y + 90),
            num_text,
            "#AAAAAA",
            waves_font_24,
            "lm"
        )
        
        
        rank += 1
    
    # 添加页脚
    img = add_footer(img)
    
    # 转换为字节
    return await convert_img(img)


async def draw_pic(roleId):
    pic = await get_square_avatar(roleId)
    pic_temp = Image.new("RGBA", pic.size)
    pic_temp.paste(pic.resize((160, 160)), (10, 10))

    avatar_mask_temp = copy.deepcopy(avatar_mask)
    mask_pic_temp = Image.new("RGBA", avatar_mask_temp.size)
    mask_pic_temp.paste(avatar_mask_temp, (-20, -45), avatar_mask_temp)

    img = Image.new("RGBA", (180, 180))
    mask_pic_temp = mask_pic_temp.resize((160, 160))
    resize_pic = pic_temp.resize((160, 160))
    img.paste(resize_pic, (0, 0), mask_pic_temp)

    return img



@timed_async_cache(
    expiration=3600,
    condition=lambda x: x,
)
async def get_char_hold_rate_data() -> Dict:
    """获取角色持有率数据"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(GET_HOLD_RATE_URL, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                return response.json().get("data", {})
    except Exception as e:
        logger.error(f"获取角色持有率数据失败: {e}")

    return {}


async def get_group_or_bot_char_hold_rate_data(group_id: str) -> Dict:
    """获取群组或者bot所有的角色持有率数据"""
    res = {}

    if group_id == "bot":
        users = await WavesBind.get_all_data()
    else:
        users = await WavesBind.get_group_all_uid(group_id)
    if not users:
        return res

    uid_fiter = {}

    # 创建用于处理并发请求的Semaphore
    semaphore = asyncio.Semaphore(20)

    async def process_uid(uid):
        """处理单个UID的数据"""
        if uid in uid_fiter:
            return None

        role_details = await get_card(uid)
        if role_details is None:
            return None

        uid_data = {}
        for role_detail in role_details:
            uid_data[role_detail.role.roleId] = role_detail.get_chain_num()

        return uid, uid_data

    # 提取所有需要处理的UID
    all_uids = []
    for user in users:
        if not user.uid:
            continue
        uids = user.uid.split("_")
        for uid in uids:
            if uid not in uid_fiter:
                all_uids.append(uid)

    # 使用Semaphore限制并发处理UID
    async def process_with_semaphore(uid):
        async with semaphore:
            return await process_uid(uid)

    # 并发执行所有UID的任务
    tasks = [process_with_semaphore(uid) for uid in all_uids]
    results = await asyncio.gather(*tasks)

    # 合并结果
    for result in results:
        if result:
            uid, uid_data = result
            uid_fiter[uid] = uid_data

    # 计算持有率
    total_player_count = len(uid_fiter)

    if total_player_count == 0:
        return res

    # 统计角色持有情况
    char_stats = {}

    for uid, chars in uid_fiter.items():
        for char_id, chain_num in chars.items():
            if char_id not in char_stats:
                char_stats[char_id] = {
                    "player_count": 0,
                    "chains": {str(i): 0 for i in range(7)},
                }

            # 增加持有人数
            char_stats[char_id]["player_count"] += 1

            # 增加对应共鸣链数量
            char_stats[char_id]["chains"][str(chain_num)] += 1

    # 构建结果数据
    char_hold_rate = []

    for char_id, stats in char_stats.items():
        player_count = stats["player_count"]
        hold_rate = round(player_count / total_player_count * 100, 1)

        # 计算共鸣链分布百分比
        chain_hold_rate = {}
        for chain, count in stats["chains"].items():
            if count > 0:
                chain_hold_rate[chain] = round(count / player_count * 100, 2)

        char_data = {
            "char_id": char_id,
            "player_count": player_count,
            "hold_rate": hold_rate,
            "chain_hold_rate": chain_hold_rate,
        }

        char_hold_rate.append(char_data)

    # 构建最终结果
    res = {"total_player_count": total_player_count, "char_hold_rate": char_hold_rate}

    return res


# 主入口函数
async def get_char_chain_hold_rate_img(ev: Event, group_id: str = "") -> Union[bytes, str]:
    """获取角色共鸣链持有率图像"""
    if group_id:
        data = await get_group_or_bot_char_hold_rate_data(group_id)
        if not data:
            return "持有率数据获取失败，请稍后再试"
    else:
        data = await get_char_hold_rate_data()
        if not data:
            return "鸣潮角色持有率数据获取失败，请稍后再试"

    return await draw_char_chain_hold_rate(ev, data, group_id=group_id)
