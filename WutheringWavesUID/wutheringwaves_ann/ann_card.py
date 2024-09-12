from pathlib import Path
from typing import Union

from PIL import Image, ImageOps, ImageDraw

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_pic, easy_paste, draw_text_by_line, easy_alpha_composite
from .main import ann
from ..utils.fonts.waves_fonts import waves_font_26, waves_font_18, waves_font_24
from ..wutheringwaves_config import WutheringWavesConfig, PREFIX

assets_dir = Path(__file__).parent / 'assets'
list_item = (
    Image.open(assets_dir / 'item.png').resize((384, 96)).convert('RGBA')
)


def filter_list(plist, func):
    return list(filter(func, plist))


async def ann_list_card() -> bytes:
    ann_list = await ann().get_ann_list()
    if not ann_list:
        raise Exception('获取游戏公告失败,请检查接口是否正常')
    grouped_ann = {}
    for item in ann_list:
        event_type = item['eventType']
        if event_type not in grouped_ann:
            grouped_ann[event_type] = []
        grouped_ann[event_type].append(item)

    bg = Image.new(
        'RGBA',
        (
            1300,
            800,
        ),
        '#f9f6f2',
    )

    for event_type, data in grouped_ann.items():
        x = 45
        if event_type == 2:
            x = 472
        elif event_type == 3:
            x = 899

        new_item = list_item.copy()
        subtitle = ann().event_type[str(event_type)]
        draw_text_by_line(
            new_item,
            (30, 30),
            subtitle,
            waves_font_24,
            '#3b4354',
            270,
            True
        )

        bg = easy_alpha_composite(
            bg, new_item, (x, 50)
        )
        for index, ann_info in enumerate(data):
            new_item = list_item.copy()
            subtitle = ann_info['postTitle']
            draw_text_by_line(
                new_item,
                (30, 30),
                subtitle,
                waves_font_24,
                '#3b4354',
                270,
            )

            draw_text_by_line(
                new_item,
                (new_item.width - 80, 10),
                str(ann_info['id']),
                waves_font_18,
                '#3b4354',
                100,
            )

            bg = easy_alpha_composite(
                bg, new_item, (x, 50 + ((index + 1) * new_item.height))
            )

    tip = (
        f'*可以使用 {PREFIX}公告#0000(右上角ID) 来查看详细内容, 例子: {PREFIX}公告#2434'
    )
    draw_text_by_line(
        bg, (0, bg.height - 35), tip, waves_font_18, '#767779', 1000, True
    )

    return await convert_img(bg)


async def ann_detail_card(ann_id: int) -> Union[bytes, str]:
    ann_list = await ann().get_ann_list()
    if not ann_list:
        raise '获取游戏公告失败,请检查接口是否正常'
    content = filter_list(ann_list, lambda x: x['id'] == ann_id)
    if not content:
        return '未找到该公告'

    postId = content[0]['postId']
    res = await ann().get_ann_detail(postId)
    if not res:
        return '未找到该公告'
    post_content = sorted(res['postContent'], key=lambda x: x['contentType'], reverse=True)
    content_type2_first = filter_list(post_content, lambda x: x['contentType'] == 2)
    if not content_type2_first and 'coverImages' in res:
        _node = res['coverImages'][0]
        _node['contentType'] = 2
        post_content.insert(0, _node)

    drow_height = 0
    for temp in post_content:
        content_type = temp['contentType']
        if content_type == 1:
            # 文案
            content = temp['content']
            (
                x_drow_duanluo,
                x_drow_note_height,
                x_drow_line_height,
                x_drow_height,
            ) = split_text(content)
            drow_height += x_drow_height
        elif content_type == 2 and 'url' in temp and temp['url'].endswith(('jpg', 'png', 'jpeg')):
            # 图片
            _size = (temp['imgWidth'], temp['imgHeight'])
            img = await get_pic(temp['url'], _size)
            img_height = img.size[1]
            if img.width > 1080:
                ratio = 1080 / img.width
                img_height = int(img.height * ratio)
            drow_height += img_height + 40

    im = Image.new('RGB', (1080, drow_height), '#f9f6f2')
    draw = ImageDraw.Draw(im)
    # 左上角开始
    x, y = 0, 0

    for temp in post_content:
        content_type = temp['contentType']
        if content_type == 1:
            # 文案
            content = temp['content']
            (
                drow_duanluo,
                drow_note_height,
                drow_line_height,
                drow_height,
            ) = split_text(content)
            for duanluo, line_count in drow_duanluo:
                draw.text((x, y), duanluo, fill=(0, 0, 0), font=waves_font_26)
                y += drow_line_height * line_count
        elif content_type == 2 and 'url' in temp and temp['url'].endswith(('jpg', 'png', 'jpeg')):
            # 图片
            _size = (temp['imgWidth'], temp['imgHeight'])
            img = await get_pic(temp['url'], _size)
            if img.width > im.width:
                ratio = im.width / img.width
                img = img.resize((int(img.width * ratio), int(img.height * ratio)))
            easy_paste(im, img, (0, y))
            y += img.size[1] + 40

    if hasattr(waves_font_26, 'getsize'):
        _x, _y = waves_font_26.getsize('囗')  # type: ignore
    else:
        bbox = waves_font_26.getbbox('囗')
        _x, _y = bbox[2] - bbox[0], bbox[3] - bbox[1]

    padding = (_x, _y, _x, _y)
    im = ImageOps.expand(im, padding, '#f9f6f2')

    return await convert_img(im)


def split_text(content: str):
    # 按规定宽度分组
    max_line_height, total_lines = 0, 0
    allText = []
    for text in content.split('\n'):
        duanluo, line_height, line_count = get_duanluo(text)
        max_line_height = max(line_height, max_line_height)
        total_lines += line_count
        allText.append((duanluo, line_count))
    line_height = max_line_height
    total_height = total_lines * line_height
    drow_height = total_lines * line_height
    return allText, total_height, line_height, drow_height


def get_duanluo(text: str):
    txt = Image.new('RGBA', (600, 800), (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)
    # 所有文字的段落
    duanluo = ''
    max_width = 1080
    # 宽度总和
    sum_width = 0
    # 几行
    line_count = 1
    # 行高
    line_height = 0
    for char in text:
        left, top, right, bottom = draw.textbbox((0, 0), char, waves_font_26)
        width, height = (right - left, bottom - top)
        sum_width += width
        if sum_width > max_width:  # 超过预设宽度就修改段落 以及当前行数
            line_count += 1
            sum_width = 0
            duanluo += '\n'
        duanluo += char
        line_height = max(height, line_height)
    if not duanluo.endswith('\n'):
        duanluo += '\n'
    return duanluo, line_height, line_count


def sub_ann(bot_id: str, group: str):
    groups = WutheringWavesConfig.get_config('WavesAnnGroups').data
    if bot_id not in groups:
        groups[bot_id] = []
    if group in groups[bot_id]:
        return '已经订阅了'
    else:
        groups[bot_id].append(group)
        WutheringWavesConfig.set_config('WavesAnnGroups', groups)
    return '成功订阅鸣潮公告'


def unsub_ann(bot_id: str, group: str):
    groups = WutheringWavesConfig.get_config('WavesAnnGroups').data
    if bot_id not in groups:
        groups[bot_id] = []
    if group in groups[bot_id]:
        groups[bot_id].remove(group)
        WutheringWavesConfig.set_config('WavesAnnGroups', groups)
        return '成功取消订阅鸣潮公告'
    else:
        return '已经不在订阅中了'
