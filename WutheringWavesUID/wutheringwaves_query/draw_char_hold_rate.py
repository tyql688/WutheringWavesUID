from typing import Dict, Tuple, Union

import httpx
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.wwapi import GET_HOLD_RATE_URL
from ..utils.ascension.char import get_char_model
from ..utils.fonts.waves_fonts import (
    waves_font_12,
    waves_font_14,
    waves_font_16,
    waves_font_20,
    waves_font_24,
    waves_font_28,
    waves_font_36,
)
from ..utils.image import (
    add_footer,
    draw_text_with_shadow,
    get_square_avatar,
    get_waves_bg,
)
from ..utils.resource.constant import SPECIAL_CHAR_NAME
from ..utils.util import timed_async_cache

# 定义颜色
BG_COLOR = (30, 33, 45)
CARD_COLOR = (49, 53, 69, 200)  # 半透明卡片
CARD_COLOR_LIGHT = (60, 65, 85, 220)  # 轻微亮一点的卡片颜色
HIGHLIGHT_COLOR = (75, 132, 221)
BAR_BG_COLOR = (60, 63, 77, 180)
TEXT_COLOR = (220, 220, 220)
TEXT_COLOR_LIGHT = (255, 255, 255)
TEXT_COLOR_DARK = (180, 180, 180)
TITLE_COLOR = (255, 255, 255)

# 颜色名称（用于draw_text_with_shadow）
WHITE = "white"
BLACK = "black"

# 星级颜色
STAR_COLORS = {
    3: (91, 150, 224),  # 3星
    4: (187, 128, 243),  # 4星
    5: (236, 185, 57),  # 5星
}

# 共鸣链颜色 - 更加鲜艳的色彩
CONSTELLATION_COLORS = [
    "#579ff2",  # 0命 - 明亮蓝色
    "#50e3c2",  # 1命 - 青色
    "#b8e986",  # 2命 - 鲜亮绿色
    "#f8e71c",  # 3命 - 黄色
    "#f5a623",  # 4命 - 橙色
    "#ff5e5e",  # 5命 - 亮红色
    "#db44ff",  # 6命 - 鲜紫色
]

# 定义尺寸
CARD_PADDING = 20
AVATAR_SIZE = 90
BAR_HEIGHT = 25  # 减小条形图高度
ITEM_HEIGHT = 140  # 进一步减小项目高度
GAP = 15


# 添加文本函数，替代导入
def add_text(
    img: Image.Image,
    pos: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
    anchor: str = "lt",
) -> None:
    """添加文本到图像上"""
    draw = ImageDraw.Draw(img)
    draw.text(pos, text, font=font, fill=fill, anchor=anchor)


# 绘制圆角矩形函数，替代导入
def draw_rounded_rectangle(
    img: Image.Image,
    xy: Tuple[int, int, int, int],
    fill: Union[Tuple[int, int, int], Tuple[int, int, int, int]],
    radius: int = 10,
) -> None:
    """绘制圆角矩形"""
    draw = ImageDraw.Draw(img)
    x1, y1, x2, y2 = xy

    # 确保坐标正确（x1 < x2, y1 < y2）
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # 检查矩形宽度和高度，自动调整半径
    width = x2 - x1
    height = y2 - y1
    radius = min(radius, width // 2, height // 2)

    if radius <= 0:
        # 如果半径小于等于0，直接绘制普通矩形
        draw.rectangle(xy, fill=fill)
        return

    # 绘制矩形主体
    draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
    draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)

    # 绘制四个角
    draw.pieslice((x1, y1, x1 + 2 * radius, y1 + 2 * radius), 180, 270, fill=fill)
    draw.pieslice((x2 - 2 * radius, y1, x2, y1 + 2 * radius), 270, 360, fill=fill)
    draw.pieslice((x1, y2 - 2 * radius, x1 + 2 * radius, y2), 90, 180, fill=fill)
    draw.pieslice((x2 - 2 * radius, y2 - 2 * radius, x2, y2), 0, 90, fill=fill)


# 创建发光效果
def create_glow_effect(
    img: Image.Image, color: Tuple[int, int, int], intensity: int = 5
) -> Image.Image:
    """为图像添加发光效果"""
    # 创建一个新图像用于发光效果
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)

    # 在透明图像上绘制对象
    mask = img.getchannel("A")

    # 创建发光
    for i in range(intensity):
        blur_radius = (i + 1) * 2
        glow_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        div_factor = i + 2
        glow_img.putalpha(
            mask.point(
                lambda x: (
                    int(x * (1 if div_factor <= 0 else 0.5 / div_factor) + 0.5)
                    if x > 0
                    else 0
                )
            )
        )

        # 给发光添加颜色
        colored_glow = Image.new("RGBA", glow_img.size, (*color, 0))
        colored_glow.putalpha(glow_img.getchannel("A"))

        # 组合发光图层
        glow = Image.alpha_composite(glow, colored_glow)

    return glow


async def get_avatar_with_style(char_id: str, star_level: int) -> Image.Image:
    """获取带有样式的角色头像"""
    avatar = await get_square_avatar(char_id)
    avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE))

    # 获取对应星级的颜色
    star_color = STAR_COLORS.get(star_level, STAR_COLORS[5])

    # 创建圆形遮罩
    mask = Image.new("L", avatar.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)

    # 应用遮罩创建圆形头像
    circular_avatar = Image.new("RGBA", avatar.size, (0, 0, 0, 0))
    circular_avatar.paste(avatar, (0, 0), mask)

    # 创建带星级边框的头像
    border_width = 4
    border_img = Image.new(
        "RGBA",
        (AVATAR_SIZE + border_width * 2, AVATAR_SIZE + border_width * 2),
        star_color,
    )
    mask_large = Image.new("L", border_img.size, 0)
    mask_draw_large = ImageDraw.Draw(mask_large)
    mask_draw_large.ellipse((0, 0, border_img.width, border_img.height), fill=255)

    # 应用遮罩创建圆形边框
    circular_border = Image.new("RGBA", border_img.size, (0, 0, 0, 0))
    circular_border.paste(border_img, (0, 0), mask_large)

    # 创建发光效果
    glow_border = create_glow_effect(circular_border, star_color, intensity=3)

    # 将头像放在边框中央
    final_img = Image.new("RGBA", border_img.size, (0, 0, 0, 0))
    final_img = Image.alpha_composite(final_img, glow_border)
    final_img = Image.alpha_composite(final_img, circular_border)
    final_img.paste(circular_avatar, (border_width, border_width), circular_avatar)

    return final_img


async def draw_character_item(
    img: Image.Image, x: int, y: int, char_data: Dict, rank: int = 0, width: int = 1200
) -> None:
    """绘制单个角色持有率项目"""
    draw = ImageDraw.Draw(img)
    char_id = char_data["char_id"]

    # 获取角色模型以获取名称和星级
    char_model = get_char_model(char_id)
    char_name = "未知角色"
    star_level = 5  # 默认为5星

    if char_model:
        char_name = SPECIAL_CHAR_NAME.get(f"{char_id}", char_model.name)
        star_level = char_model.starLevel

    # 获取星级颜色
    star_color = STAR_COLORS.get(star_level, STAR_COLORS[5])

    # 角色持有率数据
    hold_rate = char_data["hold_rate"]
    chain_data = char_data["chain_hold_rate"]

    # 绘制渐变卡片背景
    gradient_start = CARD_COLOR
    gradient_end = CARD_COLOR_LIGHT

    # 创建一个新的RGBA图像用于渐变背景
    card_bg = Image.new("RGBA", (width, ITEM_HEIGHT), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_bg)

    # 在新图像上绘制渐变
    for i in range(ITEM_HEIGHT):
        # 计算当前位置的颜色
        blend_factor = i / ITEM_HEIGHT
        current_color = (
            int(
                gradient_start[0] * (1 - blend_factor) + gradient_end[0] * blend_factor
            ),
            int(
                gradient_start[1] * (1 - blend_factor) + gradient_end[1] * blend_factor
            ),
            int(
                gradient_start[2] * (1 - blend_factor) + gradient_end[2] * blend_factor
            ),
            int(
                gradient_start[3] * (1 - blend_factor) + gradient_end[3] * blend_factor
            ),
        )
        # 绘制横线
        card_draw.line([(0, i), (width, i)], fill=current_color)

    # 创建圆角遮罩
    mask = Image.new("L", (width, ITEM_HEIGHT), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, width, ITEM_HEIGHT), 15, fill=255)

    # 应用遮罩
    card_bg.putalpha(mask)

    # 将渐变背景粘贴到主图像
    img.paste(card_bg, (x, y), card_bg)

    # 绘制排名标识（如果有）
    if rank > 0:
        # 创建排名圆形背景
        rank_size = 40
        rank_x = x + 30
        rank_y = y + ITEM_HEIGHT // 2 - 10

        # 根据排名调整颜色
        if rank == 1:
            rank_bg_color = (255, 215, 0, 220)  # 金色
            glow_color = (255, 200, 0)  # 金色光晕
        elif rank == 2:
            rank_bg_color = (192, 192, 192, 220)  # 银色
            glow_color = (200, 200, 200)  # 银色光晕
        elif rank == 3:
            rank_bg_color = (205, 127, 50, 220)  # 铜色
            glow_color = (200, 130, 50)  # 铜色光晕
        else:
            rank_bg_color = (60, 60, 70, 220)
            glow_color = (80, 80, 100)  # 蓝灰色光晕

        # 创建排名图标
        rank_icon = Image.new("RGBA", (rank_size * 2, rank_size * 2), (0, 0, 0, 0))
        rank_draw = ImageDraw.Draw(rank_icon)

        # 绘制圆形背景
        rank_draw.ellipse(
            (rank_size // 2, rank_size // 2, rank_size * 3 // 2, rank_size * 3 // 2),
            fill=rank_bg_color,
        )

        # 添加发光效果
        if rank <= 3:  # 只为前三名添加发光效果
            for i in range(1, 4):
                # 绘制外圈光环
                glow_alpha = 150 - i * 40  # 从150逐渐减小透明度
                glow_width = i * 3
                rank_draw.ellipse(
                    (
                        rank_size // 2 - glow_width,
                        rank_size // 2 - glow_width,
                        rank_size * 3 // 2 + glow_width,
                        rank_size * 3 // 2 + glow_width,
                    ),
                    outline=(*glow_color, glow_alpha),
                    width=2,
                )

        # 绘制排名文字
        rank_text = f"#{rank}"
        font = waves_font_20
        text_width = font.getlength(rank_text)
        text_height = font.size
        rank_draw.text(
            (rank_size, rank_size),
            rank_text,
            font=font,
            fill=(255, 255, 255, 255),
            anchor="mm",
        )

        # 粘贴到主图像上
        img.paste(rank_icon, (rank_x - rank_size, rank_y - rank_size), rank_icon)

        # 调整头像位置
        avatar_x = x + 85
    else:
        avatar_x = x + 40

    # 获取角色头像
    avatar = await get_avatar_with_style(char_id, star_level)

    # 绘制头像 - 垂直居中
    avatar_y = y + (ITEM_HEIGHT - avatar.height) // 2
    img.paste(avatar, (avatar_x, avatar_y), avatar)

    # 绘制角色名称和星级 - 调整位置
    name_width = 180  # 限制名称显示区域宽度
    name_x = avatar_x + avatar.width + 20
    name_y = avatar_y + 20  # 根据头像位置调整

    # 绘制名称带有增强阴影效果
    draw_text_with_shadow(
        draw,
        char_name,
        name_x,
        name_y,
        waves_font_24,
        WHITE,
        BLACK,
        (1, 1),
        "lm",
    )

    # 绘制星级
    star_text = "★" * star_level
    # 对于星级颜色，我们将颜色元组转换成hex字符串
    star_color_hex = f"#{star_color[0]:02x}{star_color[1]:02x}{star_color[2]:02x}"
    draw_text_with_shadow(
        draw,
        star_text,
        name_x,
        name_y + 30,
        waves_font_16,
        star_color_hex,
        BLACK,
        (1, 1),
        "lm",
    )

    # 调整持有率位置 - 移到名称右侧，确保不重叠
    rate_x = name_x + name_width + 20  # 在名称后面留出间距
    rate_y = name_y + 15  # 垂直居中

    # 绘制持有率条形图
    bar_width = 220  # 保持宽度
    bar_x = rate_x + 70  # 紧跟在百分比后面
    bar_y = rate_y  # 与持有率文本对齐

    # 绘制持有率百分比 - 使用带有辉光效果的文本
    rate_text = f"{hold_rate}%"

    # 绘制文本辉光效果 - 使用星级颜色
    glow_color = star_color
    # 创建简单的辉光效果
    for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
        add_text(
            img,
            (rate_x + offset[0], rate_y + offset[1]),
            rate_text,
            waves_font_28,
            (*glow_color, 50),
            "mm",
        )

    # 绘制主文本
    draw_text_with_shadow(
        draw,
        rate_text,
        rate_x,
        rate_y,
        waves_font_28,
        WHITE,
        BLACK,
        (1, 1),
        "mm",
    )

    # 绘制条形图背景 - 添加纹理效果
    bar_bg = Image.new("RGBA", (bar_width, BAR_HEIGHT), (0, 0, 0, 0))
    bar_bg_draw = ImageDraw.Draw(bar_bg)

    # 绘制条形图背景
    bar_bg_draw.rounded_rectangle(
        (0, 0, bar_width, BAR_HEIGHT), BAR_HEIGHT // 2, fill=BAR_BG_COLOR
    )

    # 添加纹理效果
    for i in range(0, bar_width, 4):
        bar_bg_draw.line([(i, 0), (i, BAR_HEIGHT)], fill=(0, 0, 0, 10))

    # 粘贴背景
    img.paste(bar_bg, (bar_x, bar_y - BAR_HEIGHT // 2), bar_bg)

    # 绘制条形图进度
    progress_width = int(bar_width * hold_rate / 100)
    if progress_width > 0:
        # 使用渐变色条
        grad_start = star_color
        grad_end = (
            min(grad_start[0] + 50, 255),
            min(grad_start[1] + 50, 255),
            min(grad_start[2] + 50, 255),
        )

        # 创建一个新的RGBA图像用于渐变进度条
        progress_bar = Image.new("RGBA", (progress_width, BAR_HEIGHT), (0, 0, 0, 0))
        progress_draw = ImageDraw.Draw(progress_bar)

        # 在新图像上绘制渐变
        for i in range(progress_width):
            # 计算当前位置的颜色
            blend_factor = i / progress_width if progress_width > 0 else 0
            current_color = (
                int(grad_start[0] * (1 - blend_factor) + grad_end[0] * blend_factor),
                int(grad_start[1] * (1 - blend_factor) + grad_end[1] * blend_factor),
                int(grad_start[2] * (1 - blend_factor) + grad_end[2] * blend_factor),
                220,
            )
            # 绘制垂直线
            progress_draw.line(
                [(i, 0), (i, BAR_HEIGHT)],
                fill=current_color,
            )

        # 创建圆角遮罩
        mask = Image.new("L", (progress_width, BAR_HEIGHT), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (0, 0, progress_width, BAR_HEIGHT), BAR_HEIGHT // 2, fill=255
        )

        # 应用遮罩
        progress_bar.putalpha(mask)

        # 将渐变进度条粘贴到主图像
        img.paste(progress_bar, (bar_x, bar_y - BAR_HEIGHT // 2), progress_bar)

    # 显示所有共鸣链分布 - 移到右侧
    constellation_title_x = bar_x + bar_width + 40
    constellation_title_y = y + 35

    # 共鸣链标题 - 添加装饰
    title_color = "#ffcc00"  # 金色标题
    draw_text_with_shadow(
        draw,
        "共鸣链分布:",
        constellation_title_x,
        constellation_title_y,
        waves_font_16,
        title_color,
        BLACK,
        (1, 1),
        "lm",
    )

    # 绘制共鸣链分布图表 - 更紧凑的布局
    constellation_height = 16
    constellation_spacing_v = 5  # 更小的垂直间距
    max_width = 60  # 更小的宽度

    # 更改为高度优先布局 - 7个共鸣链分为3+4两列
    first_column_count = 4  # 第一列显示0-3命
    second_column_count = 3  # 第二列显示4-6命

    # 计算位置
    first_column_x = constellation_title_x
    second_column_x = constellation_title_x + max_width + 75  # 减小列间距

    # 共鸣链文本宽度
    c_text_width = 25  # 缩小

    # 获取共鸣链总数用于计算百分比
    total_constellation = 0
    for i in range(7):
        if str(i) in chain_data:
            total_constellation += chain_data[str(i)]

    # 绘制每个共鸣链的分布
    for i in range(7):
        c_key = str(i)
        c_value = chain_data.get(c_key, 0)
        c_percent = c_value if total_constellation == 0 else (c_value / 100) * 100

        # 确定当前共鸣链显示位置
        if i < first_column_count:  # 0-3命显示在第一列
            current_x = first_column_x
            row_index = i
        else:  # 4-6命显示在第二列
            current_x = second_column_x
            row_index = i - first_column_count

        # 计算y位置
        current_y = (
            constellation_title_y
            + 25
            + row_index * (constellation_height + constellation_spacing_v)
        )

        # 计算条形图宽度
        c_width = int(max_width * (c_percent / 100))

        # 获取共鸣链颜色
        c_color_hex = CONSTELLATION_COLORS[i]

        # 绘制共鸣链文本
        draw_text_with_shadow(
            draw,
            f"{i}链",
            current_x,
            current_y,
            waves_font_14,
            c_color_hex,
            BLACK,
            (1, 1),
            "lm",
        )

        # 绘制共鸣链条形图
        if c_width > 0:
            # 将颜色从HEX转换为RGB
            r = int(c_color_hex.lstrip("#")[0:2], 16)
            g = int(c_color_hex.lstrip("#")[2:4], 16)
            b = int(c_color_hex.lstrip("#")[4:6], 16)
            c_color = (r, g, b, 255)

            # 创建新的图像用于共鸣链条形图
            c_bar = Image.new("RGBA", (c_width, constellation_height), (0, 0, 0, 0))
            c_bar_draw = ImageDraw.Draw(c_bar)

            # 绘制渐变填充
            for i in range(c_width):
                # 渐变从左到右，颜色渐亮
                blend_factor = i / c_width if c_width > 0 else 0
                light_factor = 0.7 + blend_factor * 0.3  # 从70%亮度到100%亮度
                current_color = (
                    int(min(r * light_factor, 255)),
                    int(min(g * light_factor, 255)),
                    int(min(b * light_factor, 255)),
                    255,
                )
                c_bar_draw.line([(i, 0), (i, constellation_height)], fill=current_color)

            # 创建圆角遮罩
            c_mask = Image.new("L", (c_width, constellation_height), 0)
            c_mask_draw = ImageDraw.Draw(c_mask)
            c_mask_draw.rounded_rectangle(
                (0, 0, c_width, constellation_height),
                constellation_height // 2,
                fill=255,
            )

            # 应用遮罩
            c_bar.putalpha(c_mask)

            # 粘贴到主图像
            img.paste(
                c_bar,
                (current_x + c_text_width, current_y - constellation_height // 2),
                c_bar,
            )

        # 绘制共鸣链百分比 - 使用短格式
        percentage_text = f"{c_value:.0f}%" if c_value >= 10 else f"{c_value:.1f}%"
        draw_text_with_shadow(
            draw,
            percentage_text,
            current_x + c_text_width + c_width + 3,  # 减小间距
            current_y,
            waves_font_12,
            c_color_hex,
            BLACK,
            (1, 1),
            "lm",
        )


async def draw_char_hold_rate(data) -> bytes:
    """绘制角色持有率列表图像"""
    # 加载数据
    char_list = data["char_hold_rate"]

    # 按持有率从高到低排序
    char_list = sorted(char_list, key=lambda x: x["hold_rate"], reverse=True)

    # 设置图像尺寸
    width = 1100
    margin = 30
    item_spacing = 15
    header_height = 150
    footer_height = 50

    # 计算所需的总高度
    total_height = (
        header_height
        + (ITEM_HEIGHT + item_spacing) * len(char_list)
        + margin * 2
        + footer_height
    )

    # 创建带背景的画布 - 使用bg9
    img = get_waves_bg(width, total_height, "bg9")
    draw = ImageDraw.Draw(img)

    # 添加半透明背景覆盖层，使内容更清晰 - 使用渐变
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # 绘制渐变背景
    for y in range(img.height):
        alpha = 140 - (y * 20 // img.height)  # 从140逐渐减少透明度
        alpha = max(80, alpha)  # 透明度下限
        overlay_draw.line([(0, y), (width, y)], fill=(*BG_COLOR, alpha))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # 绘制标题背景 - 添加更明显的渐变效果
    header_bg = Image.new("RGBA", (width - margin * 2, header_height), (0, 0, 0, 0))
    header_draw = ImageDraw.Draw(header_bg)

    # 绘制渐变标题背景
    for i in range(header_height):
        alpha = 220 - int(i * 130 / header_height)  # 从220逐渐减小到90
        # 渐变颜色从深到浅
        r = BG_COLOR[0] + int(20 * i / header_height)
        g = BG_COLOR[1] + int(20 * i / header_height)
        b = BG_COLOR[2] + int(20 * i / header_height)
        header_draw.line([(0, i), (width - margin * 2, i)], fill=(r, g, b, alpha))

    # 添加圆角效果
    header_mask = Image.new("L", (width - margin * 2, header_height), 0)
    header_mask_draw = ImageDraw.Draw(header_mask)
    header_mask_draw.rounded_rectangle(
        (0, 0, width - margin * 2, header_height), 20, fill=255
    )

    header_bg.putalpha(header_mask)
    img.paste(header_bg, (margin, margin), header_bg)

    # 绘制标题 - 添加光晕效果
    title = "鸣潮角色持有率列表"
    title_x = width // 2
    title_y = margin + 50

    # 添加光晕 - 使用简单的辉光效果
    for offset in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
        add_text(
            img,
            (title_x + offset[0], title_y + offset[1]),
            title,
            waves_font_36,
            (200, 200, 255, 80),
            "mm",
        )

    # 主标题文本
    draw_text_with_shadow(
        draw,
        title,
        title_x,
        title_y,
        waves_font_36,
        WHITE,
        BLACK,
        (2, 2),
        "mm",
    )

    # 绘制角色列表项
    current_y = margin + header_height + item_spacing
    for idx, char_data in enumerate(char_list):
        await draw_character_item(
            img, margin, current_y, char_data, idx + 1, width - margin * 2
        )
        current_y += ITEM_HEIGHT + item_spacing

    # 添加页脚
    img = add_footer(img)

    # 转换为字节
    return await convert_img(img)


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


# 主入口函数
async def get_char_hold_rate_img() -> Union[bytes, str]:
    """获取角色持有率图像"""
    data = await get_char_hold_rate_data()
    if not data:
        return "持有率数据获取失败，请稍后再试"
    return await draw_char_hold_rate(data)
