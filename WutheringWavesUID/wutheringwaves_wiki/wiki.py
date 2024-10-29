import copy
from io import BytesIO
from pathlib import Path
from typing import Dict, Union, List

import httpx
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img
from gsuid_core.utils.image.utils import sget
from ..utils.api.api import WIKI_DETAIL_URL, WIKI_ENTRY_DETAIL_URL, WIKI_CATALOGUE_MAP
from ..utils.fonts.waves_fonts import waves_font_70, waves_font_30, waves_font_24, waves_font_40, waves_font_origin
from ..utils.image import get_waves_bg, add_footer, GOLD, GREY, SPECIAL_GOLD, get_weapon_type, get_crop_waves_bg, \
    get_attribute_prop, WAVES_ECHO_MAP, get_attribute_effect, change_color
from ..utils.weapon_detail import get_weapon_star

TEXT_PATH = Path(__file__).parent / 'texture2d'

QUERY_ROLE_TYPE = {
    '命座': '1',
    '天赋': '2',
}


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


async def draw_wiki_detail(query_type: str, name: str, query_role_type: str = None):
    noi = f"[鸣潮] 暂无【{name}】对应{query_type}wiki"
    if query_type not in WIKI_CATALOGUE_MAP:
        return noi

    res = await Wiki().get_entry_detail(name, WIKI_CATALOGUE_MAP[query_type])
    if not res:
        return noi

    if query_type == "共鸣者":
        return await draw_wiki_char(res['data'], query_role_type)
    elif query_type == "武器":
        return await draw_wiki_weapon(res['data'])
    elif query_type == "声骸":
        return await draw_wiki_echo(name, res['data'])


async def draw_wiki_echo(name, raw_data: Dict):
    content = raw_data['content']
    # 基础信息
    base_data = next((i for i in content['modules'] if i['title'] == '基本信息' or i['title'] == '基础信息'), None)
    if not base_data:
        return "暂无该声骸wiki"
    # 声骸技能
    skill_data = next((i for i in content['modules'] if i['title'] == '声骸技能'), None)
    if skill_data:
        skill_data = next((i for i in skill_data['components'] if i['title'] == '声骸技能'), None)
    else:
        skill_data = next((i for i in base_data['components'] if i['title'] == '声骸技能'), None)
    card_img = get_crop_waves_bg(950, 420, 'bg2')

    # 声骸展示
    echo_show_data = next((i for i in base_data['components'] if i['title'] == '声骸展示'), None)
    # 声骸信息
    echo_data = next((i for i in base_data['components'] if i['title'] == '声骸信息'), None)

    echo_image = Image.new('RGBA', (350, 400), (255, 255, 255, 0))
    echo_image_draw = ImageDraw.Draw(echo_image)
    echo_image_draw.rectangle([20, 20, 330, 380], fill=(0, 0, 0, int(0.4 * 255)))
    soup = BeautifulSoup(echo_show_data['content'], 'html.parser')
    # echo 图片
    echo_pic = Image.open(BytesIO((await sget(soup.find_all('img')[0]['src'])).content)).convert('RGBA')
    echo_pic = crop_center_img(echo_pic, 230, 230)
    echo_image.alpha_composite(echo_pic, (50, 20))

    card_img_draw = ImageDraw.Draw(card_img)
    card_img_draw.text((370, 50), f'{name}', GOLD, waves_font_40, 'lm')

    # 部分效果
    soup = BeautifulSoup(echo_data['content'], 'html.parser')
    effect = []
    rows = []
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
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
    weapon_bg = Image.open(TEXT_PATH / 'weapon_bg.png')
    echo_bg_temp = Image.new('RGBA', weapon_bg.size)
    echo_bg_temp.alpha_composite(weapon_bg, dest=(0, 0))
    echo_bg_temp_draw = ImageDraw.Draw(echo_bg_temp)
    for index, row in enumerate(rows):
        echo_bg_temp_draw.text((100, 207 + index * 50), f'{row[0]}', 'white', waves_font_30, 'lm')
        echo_bg_temp_draw.text((450, 207 + index * 50), f'{row[1]}', 'white', waves_font_30, 'rm')

    echo_bg_temp = echo_bg_temp.resize((350, 175))
    echo_image.alpha_composite(echo_bg_temp, (10, 200))

    # 合鸣效果
    for index, e in enumerate(effect):
        color = WAVES_ECHO_MAP.get(e)
        if not color:
            continue
        effect_image = await get_attribute_effect(e)
        effect_image = effect_image.resize((30, 30))
        effect_image = await change_color(effect_image, color)
        echo_image.alpha_composite(effect_image, (250, 20 + index * 20))
        # echo_image_draw.text((250, 20 + index * 20), f'{e}', color, waves_font_18, 'lm')

    # 明细
    detail_image = Image.new('RGBA', (600, 270), (255, 255, 255, 0))
    detail_image_draw = ImageDraw.Draw(detail_image)
    detail_image_draw.rounded_rectangle([20, 20, 580, 250], radius=20, fill=(0, 0, 0, int(0.3 * 255)))

    detail_image = draw_html_text(skill_data['tabs'][0]['content'], waves_font_origin, detail_image,
                                  default_font_color='rgb(255, 255, 255)',
                                  padding=(40, 30),
                                  column_spacing=0,
                                  line_spacing=20,
                                  auto_line_spacing=5,
                                  forbid_color=['rgb(0, 0, 0)', 'rgb(24, 24, 24)'])
    card_img.alpha_composite(detail_image, (330, 80))

    card_img.alpha_composite(echo_image, (0, 0))
    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img


async def draw_wiki_weapon(raw_data: Dict):
    name = raw_data['name']
    content = raw_data['content']
    # 武器信息
    weapon_data = next((i for i in content['modules'] if i['title'] == '武器信息'), None)
    if not weapon_data:
        return "暂无该武器wiki"
    # 突破材料
    upgrade_data = next((i for i in content['modules'] if i['title'] == '突破材料'), None)
    # 基础信息
    base_data = next((i for i in weapon_data['components'] if i['title'] == '基础信息'), None)
    # 武器描述
    weapon_detail = next((i for i in weapon_data['components'] if i['title'] == '武器描述'), None)
    # 角色统计
    weapon_statistics = next((i for i in weapon_data['components'] if i['type'] == 'tabs-component'), None)
    # 突破材料
    upgrade_detail_data = next((i for i in upgrade_data['components'] if i['title'] == '突破材料'), None)
    weapon_image = Image.new('RGBA', (350, 400), (255, 255, 255, 0))

    card_img = get_crop_waves_bg(950, 420, 'bg2')
    # card_img = Image.new('RGBA', (950, 520), (0, 0, 0, 255))
    await parse_weapon_base_content(base_data['content'], weapon_image, card_img)
    await parse_weapon_statistic_content(weapon_statistics['tabs'][-1]['content'], weapon_image)
    await parse_weapon_detail_content(weapon_detail['content'], card_img)
    await parse_weapon_material_content(upgrade_detail_data['content'], card_img)
    card_img.alpha_composite(weapon_image, (0, 0))
    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img


async def parse_weapon_base_content(content, image, card_img):
    # 解析HTML内容
    soup = BeautifulSoup(content, 'html.parser')
    # 提取名称
    weapon_name = soup.find('td', text='名称').find_next_sibling('td').text

    # 提取“武器类型”
    weapon_type = soup.find('td', text='武器类型').find_next_sibling('td').text

    # 提取“稀有度”
    rarity_pic = soup.find('td', text='稀有度').find_next_sibling('td').find('img')['src']
    rarity_pic = Image.open(BytesIO((await sget(rarity_pic)).content)).convert('RGBA')
    rarity_pic = rarity_pic.resize((180, int(180 / rarity_pic.size[0] * rarity_pic.size[1])))
    # weapon 图片
    weapon_pic = Image.open(BytesIO((await sget(soup.find_all('img')[0]['src'])).content)).convert('RGBA')
    weapon_pic = crop_center_img(weapon_pic, 110, 110)
    weapon_pic_bg = get_weapon_icon_bg(get_weapon_star(weapon_name))
    weapon_pic_bg.paste(weapon_pic, (10, 20), weapon_pic)
    weapon_pic_bg = weapon_pic_bg.resize((250, 250))

    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 330, 380], fill=(0, 0, 0, int(0.4 * 255)))

    image.alpha_composite(weapon_pic_bg, (50, 20))

    weapon_type = await get_weapon_type(weapon_type)
    weapon_type = weapon_type.resize((80, 80)).convert('RGBA')
    card_img_draw = ImageDraw.Draw(card_img)
    card_img_draw.text((420, 100), f'{weapon_name}', GOLD, waves_font_40, 'lm')
    card_img.alpha_composite(rarity_pic, (400, 20))
    card_img.alpha_composite(weapon_type, (340, 40))


async def parse_weapon_statistic_content(content, weapon_image):
    # 解析HTML内容
    soup = BeautifulSoup(content, 'html.parser')

    # 提取表格数据
    rows = []
    p_tags = [tag for tag in soup.find_all(True) if tag.name == 'p']
    # logger.info(f"p_tags : {p_tags}")
    # 遍历所有的<p>标签
    for p in p_tags:
        text = p.get_text(strip=True)
        # 假设每个<p>标签的文本都包含一个冒号，我们可以使用冒号来分割标签文本
        text = text.replace("：", ":")
        if ':' in text:
            key, value = text.split(':', 1)
            rows.append([key.strip(), value.strip()])
    # logger.info(f"rows : {rows}")
    weapon_bg = Image.open(TEXT_PATH / 'weapon_bg.png')
    weapon_bg_temp = Image.new('RGBA', weapon_bg.size)
    weapon_bg_temp.alpha_composite(weapon_bg, dest=(0, 0))
    weapon_bg_temp_draw = ImageDraw.Draw(weapon_bg_temp)
    for index, row in enumerate(rows):
        stats_main = await get_attribute_prop(row[0])
        stats_main = stats_main.resize((40, 40))
        weapon_bg_temp.alpha_composite(stats_main, (65, 187 + index * 50))
        weapon_bg_temp_draw.text((130, 207 + index * 50), f'{row[0]}', 'white', waves_font_30, 'lm')
        weapon_bg_temp_draw.text((500, 207 + index * 50), f'{row[1]}', 'white', waves_font_30, 'rm')

    weapon_bg_temp = weapon_bg_temp.resize((350, 175))
    weapon_image.alpha_composite(weapon_bg_temp, (10, 200))


async def parse_weapon_detail_content(content, card_img):
    image = Image.new('RGBA', (600, 270), (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(image)
    image_draw.rounded_rectangle([20, 20, 580, 250], radius=20, fill=(0, 0, 0, int(0.3 * 255)))

    image = draw_html_text(content, waves_font_origin, image, default_font_color='rgb(255, 255, 255)', padding=(40, 30),
                           line_spacing=20, auto_line_spacing=5)
    card_img.alpha_composite(image, (330, 130))


def get_weapon_icon_bg(star: int = 3) -> Image.Image:
    if star < 3:
        star = 3
    bg_path = TEXT_PATH / f'weapon_icon_bg_{star}.png'
    bg_img = Image.open(bg_path)
    bg_img = Image.new('RGBA', bg_img.size)
    return bg_img


async def parse_weapon_material_content(content, card_img):
    # 解析HTML
    soup = BeautifulSoup(content, 'html.parser')

    # 找到包含"80级"的单元格
    td = soup.find(string="80级").find_parent('td')

    material_img = Image.new('RGBA', (300, 150))
    material_img_draw = ImageDraw.Draw(material_img)
    material_img_draw.rounded_rectangle([20, 20, 280, 130], radius=20, fill=(0, 0, 0, int(0.3 * 255)))
    material_img_draw.text((40, 20), f'突破材料', GOLD, waves_font_origin(24), 'lm')
    next_td = td.find_next_sibling('td')
    index = 0
    while next_td:
        # 找到td中的所有img元素
        imgs = next_td.find_all('img')
        for idx, img in enumerate(imgs):
            material = Image.open(BytesIO((await sget(img['src'])).content)).convert('RGBA')
            material = material.resize((70, 70))
            material_img.alpha_composite(material, (30 + index * 80, 50))
            index += 1
        # 移动到下一个兄弟td
        next_td = next_td.find_next_sibling('td')

    # card_img.alpha_composite(material_img, (330, 350))
    card_img.alpha_composite(material_img, (650, 30))


async def draw_wiki_char(raw_data: Dict, query_role_type: str):
    name = raw_data['name']
    names = name.split('-')
    if len(names) > 1:
        name = names[0] + '-' + names[2]
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
    # 技能介绍
    skill_data = next((i for i in char_data['components'] if i['title'] == '技能介绍'), None)

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

    card_img = get_waves_bg(1000, 2180, 'bg2')

    if query_role_type == "天赋":
        # 技能
        skill_height = 610
        images = []
        for index, tab in enumerate(skill_data['tabs']):
            image = draw_html_text2(tab['content'], waves_font_origin, image_width=1000,
                                    default_font_color='rgb(255, 255, 255)',
                                    padding=(40, 30),
                                    line_spacing=20, auto_line_spacing=5, background_color=(255, 255, 255, 0),
                                    init_padding=(210, 0))
            soup = BeautifulSoup(tab['content'], 'html.parser')
            skill_image = soup.find('img')['src']
            skill_image = Image.open(BytesIO((await sget(skill_image)).content)).convert('RGBA')
            images.append((tab['title'], skill_image, image))
            skill_height += image.size[1]

        card_img = get_waves_bg(1000, skill_height + 100, 'bg2')
        card_draw = ImageDraw.Draw(card_img)

        skill_height = 610
        index = 0
        for name, skill_image, image in images:
            mz_bg = Image.open(TEXT_PATH / 'mz_bg.png')
            mz_bg_temp = Image.new('RGBA', mz_bg.size)
            chain = await change_white_color(skill_image)
            chain = chain.resize((100, 100))
            mz_bg.paste(chain, (95, 75), chain)
            mz_bg_temp.alpha_composite(mz_bg, dest=(0, 0))

            card_img.alpha_composite(image, (0, 20 + skill_height))
            card_img.alpha_composite(mz_bg_temp, (0, 70 + skill_height))
            card_draw.text((70, skill_height + 70), name, fill=SPECIAL_GOLD, font=waves_font_40, anchor='lm')
            index += 1
            skill_height += image.size[1]

    else:
        # 命座 共鸣链
        mz_bg = await parse_mz_content(mz_data['content'])
        card_img.alpha_composite(mz_bg, (0, 600))

    char_bg.alpha_composite(char_pic, (0, 0))
    char_bg.alpha_composite(role_statistic_pic, (580, 220))
    card_img.paste(char_bg, (0, -5), char_bg)
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
        # temp = {'name': columns[0].text.strip(), 'effect': columns[1].text.strip()}
        temp = {
            'name': columns[0].text.strip(),
            'effect': [collect_text_and_style(columns[1], parent_font_size=24, is_force_parent_font_size=True,
                                              parent_color='rgb(255, 255, 255)')]
        }
        # 如果单元格中有图像
        img_tag = columns[0].find('img')
        if img_tag:
            temp['url'] = img_tag['src']
        # 将结果添加到列表
        data.append(temp)

    image = Image.new('RGBA', (1000, 1550), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 980, 1530], fill=(0, 0, 0, int(0.3 * 255)))

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
        # draw_text_by_line(
        #     image,
        #     (250, 150 + index * 250),
        #     _data['effect'],
        #     waves_font_24,
        #     "white",
        #     550,
        #     False
        # )
        draw_text(_data['effect'], waves_font_origin, image=image, padding=(0, 0),
                  init_padding=(250, 150 + index * 250), max_line_width=950, column_spacing=0)
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


def draw_html_text(html_content, font_origin, image=None, image_width=500, image_height=600,
                   background_color=(255, 255, 255, 255), text_align='left', padding=(10, 10),
                   line_spacing=5, column_spacing=5, auto_line_spacing=5,
                   default_font_size=16,
                   default_font_color='rgb(0, 0, 0)',
                   is_force_parent_color=False,
                   is_force_parent_font_size=False,
                   forbid_color: Union[str, List] = 'rgb(0, 0, 0)'):
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
    soup = BeautifulSoup(html_content, 'html.parser')

    # 创建或使用现有的图像对象
    if image is None:
        image = Image.new("RGBA", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    y_offset = padding[1]  # 开始绘制的Y偏移，根据边距设置
    max_line_width = image.size[0] - int(padding[0] * 1.5)  # 文本的最大宽度

    # 递归函数处理嵌套的 <span>，并直接绘制文本
    def collect_text_and_style(element, parent_color=default_font_color, parent_font_size=default_font_size,
                               is_force_parent_color=is_force_parent_color,
                               is_force_parent_font_size=is_force_parent_font_size,
                               forbid_color=forbid_color):
        segments = []
        font_size = parent_font_size  # 默认使用父级字体大小
        color = parent_color  # 默认使用父级颜色

        # 获取样式
        style = element.get('style')
        if style:
            styles = style.split(';')
            for s in styles:
                if 'font-size' in s and not is_force_parent_font_size:
                    font_size = int(s.split(':')[1].strip().replace('px', ''))
                elif 'color' in s and not is_force_parent_color:
                    _color = s.split(':')[1].strip()
                    if isinstance(forbid_color, str) and _color != forbid_color:
                        color = _color
                    if isinstance(forbid_color, list) and _color not in forbid_color:
                        color = _color

        # 转换颜色为RGB格式
        rgb_color = tuple(map(int, color.replace('rgb(', '').replace(')', '').split(',')))

        # 获取该标签中的文本和子元素
        for content in element.children:
            if isinstance(content, str):
                if content:
                    segments.append((content.strip(), font_size, rgb_color))  # 收集文本块及其样式
            elif content.name == 'br':
                segments.append(('\n', font_size, rgb_color))
            else:
                # 对于非字符串内容，递归处理子元素
                nested_segments = collect_text_and_style(content, color, font_size, is_force_parent_color,
                                                         is_force_parent_font_size, forbid_color)
                segments.extend(nested_segments)  # 将子元素的段落添加到列表中

        return segments

    # 遍历所有的 <p> 标签，处理其中的 <span> 标签
    for p in soup.find_all('p'):
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
                    current_line = ''
                    for word in text:
                        current_line_bbox = draw.textbbox((0, 0), current_line, font=font_origin(font_size))
                        current_line_bbox_width = current_line_bbox[2] - current_line_bbox[0]
                        if x_offset + current_line_bbox_width > max_line_width:
                            if current_line:
                                draw.text((x_offset, y_offset), current_line, font=font_origin(font_size),
                                          fill=rgb_color)
                            y_offset += font_size + auto_line_spacing
                            x_offset = padding[0]
                            current_line = word
                        else:
                            current_line += word
                    if current_line:
                        draw.text((x_offset, y_offset), current_line, font=font_origin(font_size),
                                  fill=rgb_color)
                        current_line_bbox = draw.textbbox((0, 0), current_line, font=font_origin(font_size))
                        current_line_bbox_width = current_line_bbox[2] - current_line_bbox[0]
                        x_offset += current_line_bbox_width
                else:
                    draw.text((x_offset, y_offset), text, font=font_origin(font_size), fill=rgb_color)
                    # 更新 x_offset，准备绘制下一个文本段
                    x_offset += text_width + column_spacing  # 增加列间距
            else:
                x_offset = padding[0]
                y_offset += font_size + line_spacing

        y_offset += font_size + line_spacing  # 更新 y_offset，保证下一行绘制

    return image


def draw_html_text2(html_content, font_origin, image=None, image_width=500,
                    background_color=(255, 255, 255, 255), text_align='left', padding=(10, 10),
                    line_spacing=5, column_spacing=0, auto_line_spacing=5,
                    default_font_size=16,
                    default_font_color='rgb(0, 0, 0)',
                    is_force_parent_color=False,
                    is_force_parent_font_size=False,
                    forbid_color='rgb(0, 0, 0)',
                    init_padding=(0, 0)):
    """
    根据 HTML 内容绘制图像文本，保持嵌套样式和布局，并支持自动换行。

    Args:
        html_content (str): 要绘制的 HTML 内容。
        font_origin (function): 自定义字体生成函数，接受字体大小作为参数。
        image (Image, optional): 可选的自定义图像对象。如果未提供，将创建新的图像。
        image_width (int): 图像的宽度，默认为800像素。
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
    soup = BeautifulSoup(html_content, 'html.parser')
    temp_image = Image.new("RGBA", (image_width, 1), background_color)
    draw = ImageDraw.Draw(temp_image)

    # 递归函数处理嵌套的 <span>，并直接绘制文本
    def collect_text_and_style(element, parent_color=default_font_color, parent_font_size=default_font_size,
                               is_force_parent_color=is_force_parent_color,
                               is_force_parent_font_size=is_force_parent_font_size,
                               forbid_color=forbid_color):
        segments = []
        font_size = parent_font_size  # 默认使用父级字体大小
        color = parent_color  # 默认使用父级颜色

        # 获取样式
        style = element.get('style')
        if style:
            styles = style.split(';')
            for s in styles:
                if 'font-size' in s and not is_force_parent_font_size:
                    font_size = int(s.split(':')[1].strip().replace('px', ''))
                elif 'color' in s and not is_force_parent_color:
                    _color = s.split(':')[1].strip()
                    if _color != forbid_color:
                        color = _color

        # 转换颜色为RGB格式
        rgb_color = tuple(map(int, color.replace('rgb(', '').replace(')', '').split(',')))

        # 获取该标签中的文本和子元素
        for content in element.children:
            if isinstance(content, str):
                if content:
                    segments.append((content.strip(), font_size, rgb_color))  # 收集文本块及其样式
            elif content.name == 'br':
                segments.append(('\n', font_size, rgb_color))
            else:
                # 对于非字符串内容，递归处理子元素
                nested_segments = collect_text_and_style(content, color, font_size, is_force_parent_color,
                                                         is_force_parent_font_size, forbid_color)
                segments.extend(nested_segments)  # 将子元素的段落添加到列表中

        return segments

    def draw_my_text(segments_in_lines, x_offset, y_offset, draw, max_line_width, is_draw=True):

        # 遍历所有的 <p> 标签，处理其中的 <span> 标签
        for segments_in_line in segments_in_lines:
            x_offset = padding[0] + init_padding[0]  # 初始 x 偏移
            # 绘制每个文本段
            for text, font_size, rgb_color in segments_in_line:
                if text.strip():  # 如果有非空文本内容
                    # 计算文本段的宽度
                    bbox = draw.textbbox((0, 0), text, font=font_origin(font_size))
                    text_width = bbox[2] - bbox[0]

                    # 如果 x_offset + 当前文本段宽度超过最大宽度，换行
                    if x_offset + text_width > max_line_width:
                        current_line = ''
                        for word in text:
                            current_line_bbox = draw.textbbox((0, 0), current_line, font=font_origin(font_size))
                            current_line_bbox_width = current_line_bbox[2] - current_line_bbox[0]
                            if x_offset + current_line_bbox_width > max_line_width:
                                if current_line:
                                    if is_draw:
                                        draw.text((x_offset, y_offset), current_line, font=font_origin(font_size),
                                                  fill=rgb_color)
                                y_offset += font_size + auto_line_spacing
                                x_offset = padding[0] + init_padding[0]
                                current_line = word
                            else:
                                current_line += word
                        if current_line:
                            if is_draw:
                                draw.text((x_offset, y_offset), current_line, font=font_origin(font_size),
                                          fill=rgb_color)
                            current_line_bbox = draw.textbbox((0, 0), current_line, font=font_origin(font_size))
                            current_line_bbox_width = current_line_bbox[2] - current_line_bbox[0]
                            x_offset += current_line_bbox_width
                    else:
                        if is_draw:
                            draw.text((x_offset, y_offset), text, font=font_origin(font_size), fill=rgb_color)
                        # 更新 x_offset，准备绘制下一个文本段
                        x_offset += text_width + column_spacing  # 增加列间距
                else:
                    x_offset = padding[0] + init_padding[0]
                    y_offset += font_size + line_spacing

            y_offset += font_size + line_spacing  # 更新 y_offset，保证下一行绘制

        return y_offset

    max_line_width = temp_image.size[0] - int(padding[0] * 1.5)  # 文本的最大宽度

    segments_in_lines = []
    for p in soup.find_all('p'):
        segments_in_line = []
        segments_in_line.extend(collect_text_and_style(p))
        segments_in_lines.append(segments_in_line)

    if not image:
        y_offset = draw_my_text(segments_in_lines, padding[0] + init_padding[0], padding[1] + init_padding[1], draw,
                                max_line_width, False)

        needed_height = y_offset + padding[1]
        image = Image.new("RGBA", (image_width, needed_height), background_color)
    draw = ImageDraw.Draw(image)

    draw_my_text(segments_in_lines, padding[0] + init_padding[0], padding[1] + init_padding[1], draw, max_line_width,
                 True)
    return image


def collect_text_and_style(element, parent_color='rgb(0, 0, 0)', parent_font_size=16, is_force_parent_color=False,
                           is_force_parent_font_size=False, forbid_color='rgb(0, 0, 0)'):
    segments = []
    font_size = parent_font_size  # 默认使用父级字体大小
    color = parent_color  # 默认使用父级颜色

    # 获取样式
    style = element.get('style')
    if style:
        styles = style.split(';')
        for s in styles:
            if 'font-size' in s and not is_force_parent_font_size:
                font_size = int(s.split(':')[1].strip().replace('px', ''))
            elif 'color' in s and not is_force_parent_color:
                _color = s.split(':')[1].strip()
                if _color != forbid_color:
                    color = _color

    # 转换颜色为RGB格式
    rgb_color = tuple(map(int, color.replace('rgb(', '').replace(')', '').split(',')))

    # 获取该标签中的文本和子元素
    for content in element.contents:
        if isinstance(content, str):
            segments.append((content, font_size, rgb_color))  # 收集文本块及其样式
        else:
            # 对于非字符串内容，递归处理子元素
            nested_segments = collect_text_and_style(content, color, font_size, is_force_parent_color,
                                                     is_force_parent_font_size, forbid_color)
            segments.extend(nested_segments)  # 将子元素的段落添加到列表中

    return segments


def draw_text(segments_in_lines, font_origin, image=None, image_width=500, image_height=600,
              background_color=(255, 255, 255, 255), padding=(10, 10),
              line_spacing=5, column_spacing=5, auto_line_spacing=5, init_padding=(0, 0), max_line_width=None):
    # 创建或使用现有的图像对象
    if image is None:
        image = Image.new("RGBA", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    y_offset = padding[1] + init_padding[1]  # 开始绘制的Y偏移，根据边距设置
    if not max_line_width:
        max_line_width = image.size[0] - int(padding[0] * 1.5)  # 文本的最大宽度

    for segments_in_line in segments_in_lines:
        x_offset = padding[0] + init_padding[0]  # 初始 x 偏移
        # 绘制每个文本段
        for text, font_size, rgb_color in segments_in_line:
            if text.strip():  # 如果有非空文本内容
                # 计算文本段的宽度
                bbox = draw.textbbox((0, 0), text, font=font_origin(font_size))
                text_width = bbox[2] - bbox[0]

                # 如果 x_offset + 当前文本段宽度超过最大宽度，换行
                if x_offset + text_width > max_line_width:
                    current_line = ''
                    for word in text:
                        current_line_bbox = draw.textbbox((0, 0), current_line, font=font_origin(font_size))
                        current_line_bbox_width = current_line_bbox[2] - current_line_bbox[0]
                        if x_offset + current_line_bbox_width > max_line_width:
                            if current_line:
                                draw.text((x_offset, y_offset), current_line, font=font_origin(font_size),
                                          fill=rgb_color)
                            y_offset += font_size + auto_line_spacing
                            x_offset = padding[0] + init_padding[0]
                            current_line = word
                        else:
                            current_line += word
                    if current_line:
                        draw.text((x_offset, y_offset), current_line, font=font_origin(font_size),
                                  fill=rgb_color)
                        current_line_bbox = draw.textbbox((0, 0), current_line, font=font_origin(font_size))
                        current_line_bbox_width = current_line_bbox[2] - current_line_bbox[0]
                        x_offset += current_line_bbox_width
                else:
                    draw.text((x_offset, y_offset), text, font=font_origin(font_size), fill=rgb_color)
                    # 更新 x_offset，准备绘制下一个文本段
                    x_offset += text_width + column_spacing  # 增加列间距

        # 完成一行后，y_offset 更新，进入下一行
        y_offset += font_size + line_spacing  # 更新 y_offset，保证下一行绘制

    return image
