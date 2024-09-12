import copy
from io import BytesIO
from pathlib import Path
from typing import Dict

import httpx
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import draw_text_by_line
from gsuid_core.utils.image.utils import sget
from ..utils.api.api import WIKI_DETAIL_URL, WIKI_ENTRY_DETAIL_URL, WIKI_CATALOGUE_MAP
from ..utils.fonts.waves_fonts import waves_font_70, waves_font_30, waves_font_24, waves_font_40
from ..utils.image import get_waves_bg, add_footer, GOLD, GREY, SPECIAL_GOLD

TEXT_PATH = Path(__file__).parent / 'texture2d'


class Wiki:
    _HEADER = {
        "source": "h5",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        'wiki_type': '9'
    }

    async def _get_wiki_catalogue(self, catalogueId: str):
        headers = copy.deepcopy(self._HEADER)
        data = {'catalogueId': catalogueId, 'limit': 1000}
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.post(WIKI_DETAIL_URL, headers=headers, data=data, timeout=10)
            return res.json()

    async def _get_entry_id(self, name: str, catalogueId: str):
        catalogue_data = await self._get_wiki_catalogue(catalogueId)
        if catalogue_data['code'] != 200:
            return
        char_record = next((i for i in catalogue_data['data']['results']['records'] if i['name'] == name), None)
        # logger.debug(f'【鸣潮WIKI】 名字:【{name}】: {char_record}')
        if not char_record:
            return

        return char_record['entryId']

    async def get_entry_detail(self, name: str, catalogueId: str):
        entry_id = await self._get_entry_id(name, catalogueId)
        if not entry_id:
            return

        headers = copy.deepcopy(self._HEADER)
        data = {'id': entry_id}
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.post(WIKI_ENTRY_DETAIL_URL, headers=headers, data=data, timeout=10)
            return res.json()


async def draw_wiki_detail(query_type: str, name: str):
    if query_type == "角色":
        query_type = "共鸣者"

    if query_type not in WIKI_CATALOGUE_MAP:
        return "暂无该类型wiki"

    res = await Wiki().get_entry_detail(name, WIKI_CATALOGUE_MAP[query_type])

    return await draw_wiki_char(res['data'])


async def draw_wiki_char(raw_data: Dict):
    name = raw_data['name']
    content = raw_data['content']
    # 基础资料
    base_data = next((i for i in content['modules'] if i['title'] == '基础资料'), None)
    if not base_data:
        return "暂无该角色wiki"
    # 角色养成
    char_data = next((i for i in content['modules'] if i['title'] == '角色养成'), None)
    # 角色组件
    role_data = next((i['role'] for i in base_data['components'] if i['type'] == 'role-component'), None)
    # 角色统计
    char_statistics = next((i for i in base_data['components'] if i['type'] == 'tabs-component'), None)
    # 共鸣链
    mz_data = next((i for i in char_data['components'] if i['type'] == 'basic-component'), None)

    char_pic = Image.open(BytesIO((await sget(role_data['figures'][0]['url'])).content)).convert('RGBA')
    char_pic = char_pic.resize((600, int(600 / char_pic.size[0] * char_pic.size[1])))

    char_bg = Image.open(BytesIO((await sget(role_data['backgroundImage'])).content)).convert('RGBA')
    char_bg = char_bg.resize((1000, int(1000 / char_bg.size[0] * char_bg.size[1])))
    char_bg_draw = ImageDraw.Draw(char_bg)
    # 名字
    char_bg_draw.text((580, 120), f'{name}', 'black', waves_font_70, 'lm')
    # syb名字
    char_bg_draw.text((580, 180), f'{role_data["subtitle"]}', GOLD, waves_font_30, 'lm')

    # 角色统计信息
    role_statistic_pic = await parse_role_statistic_content(char_statistics['tabs'][-1]['content'])

    # 命座 共鸣链
    mz_bg = await parse_mz_content(mz_data['content'])

    card_img = get_waves_bg(1000, 2180, 'bg2')

    char_bg.alpha_composite(char_pic, (0, 0))
    char_bg.alpha_composite(role_statistic_pic, (580, 220))
    card_img.paste(char_bg, (0, -5), char_bg)
    card_img.alpha_composite(mz_bg, (0, 600))

    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img


async def parse_role_statistic_content(content):
    # 解析HTML内容
    soup = BeautifulSoup(content, 'html.parser')

    # 提取表格数据
    rows = []
    table = soup.find('table')
    for tr in table.find_all('tr'):
        row = []
        for td in tr.find_all('td'):
            cell_text = td.get_text(strip=True)
            row.append(cell_text)
        if row:
            rows.append(row)

    new_rows = []
    for i in range(2):
        for j in rows:
            key = j[0 + i * 2]
            value = j[1 + i * 2]
            if key == '满突破' or key == '满突破':
                continue
            new_rows.append((key, value))
    rows = new_rows

    col_count = sum(len(row) for row in rows)
    cell_width = 400
    cell_height = 40
    table_width = cell_width
    table_height = col_count * cell_height

    image = Image.new('RGBA', (table_width, table_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    # 绘制表格
    for row_index, row in enumerate(rows):
        for col_index, cell in enumerate(row):
            # 计算单元格位置
            x0 = col_index * cell_width / 2
            y0 = row_index * cell_height
            x1 = x0 + cell_width / 2
            y1 = y0 + cell_height

            # 绘制矩形边框
            _i = 0.8 if row_index % 2 == 0 else 1
            draw.rectangle([x0, y0, x1, y1], fill=(40, 40, 40, int(_i * 255)), outline=GREY)

            # 计算文本位置以居中
            bbox = draw.textbbox((0, 0), cell, font=waves_font_24)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x0 + (cell_width / 2 - text_width) / 2
            text_y = y0 + (cell_height - text_height) / 2

            # 绘制文本
            draw.text((text_x, text_y), cell, fill="white", font=waves_font_24)

    return image


async def parse_mz_content(content):
    # 解析HTML内容
    soup = BeautifulSoup(content, 'html.parser')

    # 找到所有表格行
    rows = soup.find_all('tr')

    # 遍历表格行，提取信息
    data = []
    for row in rows[1:]:  # 跳过标题行
        columns = row.find_all('td')
        temp = {'name': columns[0].text.strip(), 'effect': columns[1].text.strip()}

        # 如果单元格中有图像
        img_tag = columns[0].find('img')
        if img_tag:
            temp['url'] = img_tag['src']
        # 将结果添加到列表
        data.append(temp)

    image = Image.new('RGBA', (1000, 1550), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([20, 20, 980, 1530], radius=20, fill=(40, 40, 40, int(1 * 255)))

    for index, _data in enumerate(data):
        mz_bg = Image.open(TEXT_PATH / 'mz_bg.png')
        mz_bg_temp = Image.new('RGBA', mz_bg.size)
        chain = Image.open(BytesIO((await sget(_data['url'])).content)).convert('RGBA')
        chain = await change_white_color(chain)
        chain = chain.resize((100, 100))
        mz_bg.paste(chain, (95, 75), chain)
        mz_bg_temp.alpha_composite(mz_bg, dest=(0, 0))
        image.alpha_composite(mz_bg_temp, (0, index * 250))

        draw.text((250, 80 + index * 250), _data['name'], fill=SPECIAL_GOLD, font=waves_font_40, anchor='lm')
        draw_text_by_line(
            image,
            (250, 150 + index * 250),
            _data['effect'],
            waves_font_24,
            "white",
            550,
            False
        )
    return image


async def change_white_color(chain):
    # 获取图像数据
    pixels = chain.load()  # 加载像素数据

    # 遍历图像的每个像素
    for y in range(chain.size[1]):  # 图像高度
        for x in range(chain.size[0]):  # 图像宽度
            # 获取当前像素的 RGBA 值
            r, g, b, a = pixels[x, y]

            # 判断是否为黑色图案的像素 (通常为 RGB = (0, 0, 0) 且 Alpha 不为 0)
            if r == 0 and g == 0 and b == 0 and a > 0:
                # 将黑色更改为白色，同时保持透明度
                pixels[x, y] = (255, 255, 255, a)

    return chain
