from io import BytesIO
from pathlib import Path
from typing import Dict, List, Union

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

from gsuid_core.utils.image.utils import sget
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.api.requests import Wiki
from ..utils.api.api import WIKI_CATALOGUE_MAP
from ..utils.fonts.waves_fonts import (
    waves_font_30,
    waves_font_40,
    waves_font_origin,
)
from ..utils.image import (
    GOLD,
    WAVES_ECHO_MAP,
    add_footer,
    get_crop_waves_bg,
    get_attribute_effect,
)

TEXT_PATH = Path(__file__).parent / "texture2d"


async def draw_wiki_detail(query_type: str, name: str):
    noi = f"[鸣潮] 暂无【{name}】对应{query_type}wiki"
    if query_type not in WIKI_CATALOGUE_MAP:
        return noi

    res = await Wiki().get_entry_detail_by_name(name, WIKI_CATALOGUE_MAP[query_type])
    if not res:
        return noi

    if query_type == "声骸":
        return await draw_wiki_echo(name, res["data"])


async def draw_wiki_echo(name, raw_data: Dict):
    content = raw_data["content"]
    # 基础信息
    base_data = next(
        (
            i
            for i in content["modules"]
            if i["title"] == "基本信息" or i["title"] == "基础信息"
        ),
        None,
    )
    if not base_data:
        return "暂无该声骸wiki"
    # 声骸技能
    skill_data = next((i for i in content["modules"] if i["title"] == "声骸技能"), None)
    if skill_data:
        skill_data = next(
            (i for i in skill_data["components"] if i["title"] == "声骸技能"), None
        )
    else:
        skill_data = next(
            (i for i in base_data["components"] if i["title"] == "声骸技能"), None
        )
    card_img = get_crop_waves_bg(950, 420, "bg2")

    # 声骸展示
    echo_show_data = next(
        (i for i in base_data["components"] if i["title"] == "声骸展示"), None
    )
    # 声骸信息
    echo_data = next(
        (i for i in base_data["components"] if i["title"] == "声骸信息"), None
    )

    echo_image = Image.new("RGBA", (350, 400), (255, 255, 255, 0))
    echo_image_draw = ImageDraw.Draw(echo_image)
    echo_image_draw.rectangle([20, 20, 330, 380], fill=(0, 0, 0, int(0.4 * 255)))
    soup = BeautifulSoup(echo_show_data["content"], "html.parser")
    # echo 图片
    echo_pic = Image.open(
        BytesIO((await sget(soup.find_all("img")[0]["src"])).content)
    ).convert("RGBA")
    echo_pic = crop_center_img(echo_pic, 230, 230)
    echo_image.alpha_composite(echo_pic, (50, 20))

    card_img_draw = ImageDraw.Draw(card_img)
    card_img_draw.text((370, 50), f"{name}", GOLD, waves_font_40, "lm")

    # 部分效果
    soup = BeautifulSoup(echo_data["content"], "html.parser")
    effect = []
    rows = []
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue
        first_cell_text = cells[0].text.strip()
        if first_cell_text in ["声骸等级", "「COST」"]:
            next_cell_text = cells[-1].text.strip() if len(cells) > 1 else ""
            # base_results[first_cell_text] = next_cell_text
            rows.append([first_cell_text.strip(), next_cell_text.strip()])
        if first_cell_text in ["合鸣效果"]:
            next_cell_text = cells[-1].text.strip() if len(cells) > 1 else ""
            effect = next_cell_text.split("、")

    # logger.info(f"rows : {rows}")
    weapon_bg = Image.open(TEXT_PATH / "weapon_bg.png")
    echo_bg_temp = Image.new("RGBA", weapon_bg.size)
    echo_bg_temp.alpha_composite(weapon_bg, dest=(0, 0))
    echo_bg_temp_draw = ImageDraw.Draw(echo_bg_temp)
    for index, row in enumerate(rows):
        echo_bg_temp_draw.text(
            (100, 207 + index * 50), f"{row[0]}", "white", waves_font_30, "lm"
        )
        echo_bg_temp_draw.text(
            (450, 207 + index * 50), f"{row[1]}", "white", waves_font_30, "rm"
        )

    echo_bg_temp = echo_bg_temp.resize((350, 175))
    echo_image.alpha_composite(echo_bg_temp, (10, 200))

    # 合鸣效果
    for index, e in enumerate(effect):
        color = WAVES_ECHO_MAP.get(e)
        if not color:
            continue
        effect_image = await get_attribute_effect(e)
        effect_image = effect_image.resize((30, 30))
        # effect_image = await change_color(effect_image, color)
        echo_image.alpha_composite(effect_image, (250, 20 + index * 20))
        # echo_image_draw.text((250, 20 + index * 20), f'{e}', color, waves_font_18, 'lm')

    # 明细
    detail_image = Image.new("RGBA", (600, 270), (255, 255, 255, 0))
    detail_image_draw = ImageDraw.Draw(detail_image)
    detail_image_draw.rounded_rectangle(
        [20, 20, 580, 250], radius=20, fill=(0, 0, 0, int(0.3 * 255))
    )

    detail_image = draw_html_text(
        skill_data["tabs"][0]["content"],
        waves_font_origin,
        detail_image,
        default_font_color="rgb(255, 255, 255)",
        padding=(40, 30),
        column_spacing=0,
        line_spacing=20,
        auto_line_spacing=5,
        forbid_color=["rgb(0, 0, 0)", "rgb(24, 24, 24)"],
    )
    card_img.alpha_composite(detail_image, (330, 80))

    card_img.alpha_composite(echo_image, (0, 0))
    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img


def draw_html_text(
    html_content,
    font_origin,
    image=None,
    image_width=500,
    image_height=600,
    background_color=(255, 255, 255, 255),
    text_align="left",
    padding=(10, 10),
    line_spacing=5,
    column_spacing=5,
    auto_line_spacing=5,
    default_font_size=16,
    default_font_color="rgb(0, 0, 0)",
    is_force_parent_color=False,
    is_force_parent_font_size=False,
    forbid_color: Union[str, List] = "rgb(0, 0, 0)",
):
    """
    根据 HTML 内容绘制图像文本，保持嵌套样式和布局，并支持自动换行。

    Args:
        html_content (str): 要绘制的 HTML 内容。
        font_origin (function): 自定义字体生成函数，接受字体大小作为参数。
        image (Image, optional): 可选的自定义图像对象。如果未提供，将创建新的图像。
        image_width (int): 图像的宽度，默认为800像素。
        image_height (int): 图像的高度，默认为600像素。
        background_color (tuple): 图像背景颜色，默认为白色。
        text_align (str): 文本对齐方式，选择 'left', 'center' 或 'right'，默认为 'left'。
        padding (tuple): 文本与图像边缘的 padding，默认为 (10, 10)。
        line_spacing (int): 行间距，默认为5像素。
        column_spacing (int): 列间距，默认为5像素。
        auto_line_spacing (int): 自动换行的行间距，默认为5像素。

    Returns:
        Image: 返回包含绘制文本的图像对象。
    """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # 创建或使用现有的图像对象
    if image is None:
        image = Image.new("RGBA", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    y_offset = padding[1]  # 开始绘制的Y偏移，根据边距设置
    max_line_width = image.size[0] - int(padding[0] * 1.5)  # 文本的最大宽度

    # 递归函数处理嵌套的 <span>，并直接绘制文本
    def collect_text_and_style(
        element,
        parent_color=default_font_color,
        parent_font_size=default_font_size,
        is_force_parent_color=is_force_parent_color,
        is_force_parent_font_size=is_force_parent_font_size,
        forbid_color=forbid_color,
    ):
        segments = []
        font_size = parent_font_size  # 默认使用父级字体大小
        color = parent_color  # 默认使用父级颜色

        # 获取样式
        style = element.get("style")
        if style:
            styles = style.split(";")
            for s in styles:
                if "font-size" in s and not is_force_parent_font_size:
                    font_size = int(s.split(":")[1].strip().replace("px", ""))
                elif "color" in s and not is_force_parent_color:
                    _color = s.split(":")[1].strip()
                    if isinstance(forbid_color, str) and _color != forbid_color:
                        color = _color
                    if isinstance(forbid_color, list) and _color not in forbid_color:
                        color = _color

        # 转换颜色为RGB格式
        rgb_color = tuple(
            map(int, color.replace("rgb(", "").replace(")", "").split(","))
        )

        # 获取该标签中的文本和子元素
        for content in element.children:
            if isinstance(content, str):
                if content:
                    segments.append(
                        (content.strip(), font_size, rgb_color)
                    )  # 收集文本块及其样式
            elif content.name == "br":
                segments.append(("\n", font_size, rgb_color))
            else:
                # 对于非字符串内容，递归处理子元素
                nested_segments = collect_text_and_style(
                    content,
                    color,
                    font_size,
                    is_force_parent_color,
                    is_force_parent_font_size,
                    forbid_color,
                )
                segments.extend(nested_segments)  # 将子元素的段落添加到列表中

        return segments

    # 遍历所有的 <p> 标签，处理其中的 <span> 标签
    for p in soup.find_all("p"):
        x_offset = padding[0]  # 初始 x 偏移
        segments_in_line = []
        # for span in p.find_all('span', recursive=False):
        segments_in_line.extend(collect_text_and_style(p))
        # 绘制每个文本段
        for text, font_size, rgb_color in segments_in_line:
            if text.strip():  # 如果有非空文本内容
                # 计算文本段的宽度
                bbox = draw.textbbox((0, 0), text, font=font_origin(font_size))
                text_width = bbox[2] - bbox[0]

                # 如果 x_offset + 当前文本段宽度超过最大宽度，换行
                if x_offset + text_width > max_line_width:
                    current_line = ""
                    for word in text:
                        current_line_bbox = draw.textbbox(
                            (0, 0), current_line, font=font_origin(font_size)
                        )
                        current_line_bbox_width = (
                            current_line_bbox[2] - current_line_bbox[0]
                        )
                        if x_offset + current_line_bbox_width > max_line_width:
                            if current_line:
                                draw.text(
                                    (x_offset, y_offset),
                                    current_line,
                                    font=font_origin(font_size),
                                    fill=rgb_color,
                                )
                            y_offset += font_size + auto_line_spacing
                            x_offset = padding[0]
                            current_line = word
                        else:
                            current_line += word
                    if current_line:
                        draw.text(
                            (x_offset, y_offset),
                            current_line,
                            font=font_origin(font_size),
                            fill=rgb_color,
                        )
                        current_line_bbox = draw.textbbox(
                            (0, 0), current_line, font=font_origin(font_size)
                        )
                        current_line_bbox_width = (
                            current_line_bbox[2] - current_line_bbox[0]
                        )
                        x_offset += current_line_bbox_width
                else:
                    draw.text(
                        (x_offset, y_offset),
                        text,
                        font=font_origin(font_size),
                        fill=rgb_color,
                    )
                    # 更新 x_offset，准备绘制下一个文本段
                    x_offset += text_width + column_spacing  # 增加列间距
            else:
                x_offset = padding[0]
                y_offset += font_size + line_spacing

        y_offset += font_size + line_spacing  # 更新 y_offset，保证下一行绘制

    return image
    return image
