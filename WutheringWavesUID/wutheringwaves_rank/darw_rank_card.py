import asyncio
import copy
from pathlib import Path
from typing import Optional, Union, List

from PIL import Image, ImageDraw
from pydantic import BaseModel

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_qq_avatar, crop_center_img
from ..utils.api.model import RoleDetailData, WeaponData
from ..utils.ascension.char import get_breach
from ..utils.calculate import get_calc_map, calc_phantom_score, get_total_score_bg
from ..utils.char_info_utils import get_all_role_detail_info_list
from ..utils.damage.abstract import DamageRankRegister
from ..utils.database.models import WavesBind
from ..utils.expression_ctx import prepare_phantom, enhance_summation_phantom_value, enhance_summation_card_value, \
    card_sort_map_to_attribute
from ..utils.fonts.waves_fonts import waves_font_18, waves_font_34, waves_font_16, waves_font_40, waves_font_30, \
    waves_font_24, waves_font_20, waves_font_44
from ..utils.image import get_waves_bg, add_footer, get_square_avatar, SPECIAL_GOLD, \
    get_square_weapon, CHAIN_COLOR, get_attribute, get_role_pile, WAVES_ECHO_MAP, get_attribute_effect, \
    change_color
from ..utils.name_convert import char_name_to_char_id, alias_to_char_name
from ..wutheringwaves_config import PREFIX

special_char = {
    "1501": ["1501", "1502"],  # 光主
    "1502": ["1501", "1502"],
    "1604": ["1604", "1605"],  # 暗主
    "1605": ["1604", "1605"],
}
special_char_name = {
    "1501": "光主",
    "1502": "光主",
    "1604": "暗主",
    "1605": "暗主",
}

card_sort_map = {
    '生命': '0',
    '攻击': '0',
    '防御': '0',
    '共鸣效率': '0%',
    '暴击': '0.0%',
    '暴击伤害': '0.0%',
    '属性伤害加成': '0.0%',
    '治疗效果加成': '0.0%',
    '普攻伤害加成': '0.0%',
    '重击伤害加成': '0.0%',
    '共鸣技能伤害加成': '0.0%',
    '共鸣解放伤害加成': '0.0%'
}
TEXT_PATH = Path(__file__).parent / 'texture2d'
TITLE_I = Image.open(TEXT_PATH / 'title.png')
TITLE_II = Image.open(TEXT_PATH / 'title2.png')
avatar_mask = Image.open(TEXT_PATH / 'avatar_mask.png')
weapon_icon_bg_3 = Image.open(TEXT_PATH / 'weapon_icon_bg_3.png')
weapon_icon_bg_4 = Image.open(TEXT_PATH / 'weapon_icon_bg_4.png')
weapon_icon_bg_5 = Image.open(TEXT_PATH / 'weapon_icon_bg_5.png')
promote_icon = Image.open(TEXT_PATH / 'promote_icon.png')
char_mask = Image.open(TEXT_PATH / 'char_mask.png')
logo_img = Image.open(TEXT_PATH / f'logo_small_2.png')


class RankInfo(BaseModel):
    roleDetail: RoleDetailData  # 角色明细
    qid: str  # qq id
    uid: int  # uid
    level: int  # 角色等级
    chain: int  # 命座
    chainName: str  # 命座
    score: float  # 角色评分
    score_bg: str  # 评分背景
    expected_damage: str  # 期望伤害
    expected_damage_int: int  # 期望伤害
    sonata_name: str  # 合鸣效果


async def find_role_detail(uid: str, char_id: Union[int, List[int]]) -> Optional[RoleDetailData]:
    role_details = await get_all_role_detail_info_list(uid)
    if role_details is None:
        return None

    # 使用生成器来进行过滤
    return next((role for role in role_details if str(role.role.roleId) in char_id), None)


async def get_rank_info_for_user(user: WavesBind, find_char_id, rankDetail):
    rankInfoList = []
    if not user.uid:
        return rankInfoList

    tasks = [find_role_detail(uid, find_char_id) for uid in user.uid.split('_')]
    role_details = await asyncio.gather(*tasks)

    for uid, role_detail in zip(user.uid.split('_'), role_details):
        if not role_detail:
            continue
        if not role_detail.phantomData or not role_detail.phantomData.equipPhantomList:
            continue

        equipPhantomList = role_detail.phantomData.equipPhantomList
        weaponData = role_detail.weaponData
        phantom_sum_value = prepare_phantom(equipPhantomList)
        phantom_sum_value = enhance_summation_phantom_value(
            find_char_id, role_detail.role.level, role_detail.role.breach,
            weaponData.weapon.weaponId, weaponData.level, weaponData.breach, weaponData.resonLevel,
            phantom_sum_value)

        # 评分
        phantom_score = 0
        calc_temp = get_calc_map(phantom_sum_value, role_detail.role.roleName)
        for i, _phantom in enumerate(equipPhantomList):
            if _phantom and _phantom.phantomProp:
                props = _phantom.get_props()
                _score, _bg = calc_phantom_score(role_detail.role.roleName, props, _phantom.cost, calc_temp)
                phantom_score += _score

        if phantom_score == 0:
            continue

        phantom_bg = get_total_score_bg(role_detail.role.roleName, phantom_score, calc_temp)

        # 面板
        temp_card_sort_map = copy.deepcopy(card_sort_map)
        card_map = enhance_summation_card_value(
            find_char_id, role_detail.role.level, role_detail.role.breach,
            role_detail.role.attributeName,
            weaponData.weapon.weaponId, weaponData.level, weaponData.breach,
            weaponData.resonLevel,
            phantom_sum_value, temp_card_sort_map
        )
        damageAttribute = card_sort_map_to_attribute(card_map)

        crit_damage, expected_damage = rankDetail['func'](damageAttribute, role_detail)

        sonata_name = ''
        for ph in phantom_sum_value.get('ph_detail', []):
            if ph['ph_num'] == 5:
                sonata_name = ph['ph_name']

        rankInfo = RankInfo(**{
            'roleDetail': role_detail,
            'qid': user.user_id,
            'uid': uid,
            'level': role_detail.role.level,
            'chain': role_detail.get_chain_num(),
            'chainName': role_detail.get_chain_name(),
            'score': round(phantom_score, 2),
            'score_bg': phantom_bg,
            'expected_damage': expected_damage,
            'expected_damage_int': int(expected_damage.replace(',', '')),
            'sonata_name': sonata_name,
        })
        rankInfoList.append(rankInfo)

    return rankInfoList


async def get_all_rank_info(users: List[WavesBind], find_char_id, rankDetail):
    tasks = [get_rank_info_for_user(user, find_char_id, rankDetail) for user in users]
    results = await asyncio.gather(*tasks)

    # Flatten the results list
    rankInfoList = [rank_info for result in results for rank_info in result]
    return rankInfoList


async def draw_rank_img(bot: Bot, ev: Event, char: str, rank_type: str):
    char_id = char_name_to_char_id(char)
    if not char_id:
        return f'[鸣潮] 角色名【{char}】无法找到, 可能暂未适配, 请先检查输入是否正确！'
    char_name = alias_to_char_name(char)

    rankDetail = DamageRankRegister.find_class(char_id)
    if not rankDetail:
        return f'[鸣潮] 角色【{char_name}排行】暂未适配伤害计算，请等待作者更新！'

    if char_id in special_char:
        find_char_id = special_char[char_id]
    else:
        find_char_id = char_id

    # 获取群里的所有拥有该角色人的数据
    users = await WavesBind.get_group_all_uid(ev.group_id)
    if not users:
        return f'[鸣潮] 群【{ev.group_id}】暂无【{char}】面板\n请使用【{PREFIX}刷新面板】后再使用此功能！'

    try:
        uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
        if uid:
            role_detail: RoleDetailData = await find_role_detail(uid, find_char_id)
            char_id = str(role_detail.role.roleId)
    except Exception as _:
        pass

    damage_title = rankDetail['title']
    rankInfoList = await get_all_rank_info(users, find_char_id, rankDetail)
    if len(rankInfoList) == 0:
        return f'[鸣潮] 群【{ev.group_id}】暂无【{char}】面板\n请使用【{PREFIX}刷新面板】后再使用此功能！'

    rankInfoList.sort(key=lambda i: (i.expected_damage_int, i.score, i.level, i.chain), reverse=True)

    rankInfoList = rankInfoList[:20]
    totalNum = len(rankInfoList)

    title_h = 500
    bar_star_h = 110
    h = title_h + totalNum * bar_star_h + 80
    card_img = get_waves_bg(1050, h, 'bg3')

    bar = Image.open(TEXT_PATH / 'bar.png')
    total_score = 0
    total_damage = 0

    tasks = [
        get_avatar(ev, rank.qid, rank.roleDetail.role.roleId) for rank in rankInfoList
    ]
    results = await asyncio.gather(*tasks)

    for index, temp in enumerate(zip(rankInfoList, results)):
        rank, role_avatar = temp
        rank: RankInfo
        role_detail: RoleDetailData = rank.roleDetail
        bar_bg = bar.copy()
        bar_star_draw = ImageDraw.Draw(bar_bg)
        # role_avatar = await get_avatar(ev, rank.qid, role_detail.role.roleId)
        bar_bg.paste(role_avatar, (100, 0), role_avatar)

        # uid
        bar_star_draw.text((210, 75), f"{rank.uid}", 'white', waves_font_20, 'lm')

        role_attribute = await get_attribute(role_detail.role.attributeName, is_simple=True)
        role_attribute = role_attribute.resize((40, 40)).convert('RGBA')
        bar_bg.alpha_composite(role_attribute, (300, 20))

        # 命座
        info_block = Image.new("RGBA", (46, 20), color=(255, 255, 255, 0))
        info_block_draw = ImageDraw.Draw(info_block)
        fill = CHAIN_COLOR[rank.chain] + (int(0.9 * 255),)
        info_block_draw.rounded_rectangle([0, 0, 46, 20], radius=6, fill=fill)
        info_block_draw.text((5, 10), f'{rank.chainName}', 'white', waves_font_18, 'lm')
        bar_bg.alpha_composite(info_block, (190, 30))

        # 等级
        info_block = Image.new("RGBA", (60, 20), color=(255, 255, 255, 0))
        info_block_draw = ImageDraw.Draw(info_block)
        info_block_draw.rounded_rectangle([0, 0, 60, 20], radius=6, fill=(54, 54, 54, int(0.9 * 255)))
        info_block_draw.text((5, 10), f'Lv.{rank.level}', 'white', waves_font_18, 'lm')
        bar_bg.alpha_composite(info_block, (240, 30))

        # 评分
        if rank.score > 0.0:
            score_bg = Image.open(TEXT_PATH / f'score_{rank.score_bg}.png')
            bar_bg.alpha_composite(score_bg, (320, 2))
            bar_star_draw.text((466, 45), f'{rank.score.__round__(1)}', 'white', waves_font_34, 'mm')
            bar_star_draw.text((466, 75), f'声骸分数', SPECIAL_GOLD, waves_font_16, 'mm')

        # 合鸣效果
        if rank.sonata_name:
            effect_image = await get_attribute_effect(rank.sonata_name)
            effect_image = effect_image.resize((60, 60))
            sonata_color = WAVES_ECHO_MAP.get(rank.sonata_name, (0, 0, 0))
            effect_image = await change_color(effect_image, sonata_color)
            bar_bg.alpha_composite(effect_image, (525, 15))
            sonata_name = rank.sonata_name
        else:
            sonata_name = '合鸣效果'
        bar_star_draw.text((558, 75), f'{sonata_name}', 'white', waves_font_16, 'mm')

        # 武器
        weapon_bg_temp = Image.new('RGBA', (600, 300))

        weaponData: WeaponData = role_detail.weaponData
        weapon_icon = await get_square_weapon(weaponData.weapon.weaponId)
        weapon_icon = crop_center_img(weapon_icon, 110, 110)
        weapon_icon_bg = get_weapon_icon_bg(weaponData.weapon.weaponStarLevel)
        weapon_icon_bg.paste(weapon_icon, (10, 20), weapon_icon)

        weapon_bg_temp_draw = ImageDraw.Draw(weapon_bg_temp)
        weapon_bg_temp_draw.text((200, 30), f'{weaponData.weapon.weaponName[:5]}', SPECIAL_GOLD, waves_font_40, 'lm')
        weapon_bg_temp_draw.text((203, 75), f'Lv.{weaponData.level}/90', 'white', waves_font_30, 'lm')

        _x = 220 + 43 * len(weaponData.weapon.weaponName)
        _y = 37
        weapon_bg_temp_draw.rounded_rectangle([_x - 15, _y - 15, _x + 50, _y + 15], radius=7,
                                              fill=(128, 138, 135, int(0.8 * 255)))
        weapon_bg_temp_draw.text((_x, _y), f'精{weaponData.resonLevel}', 'white',
                                 waves_font_24, 'lm')

        weapon_breach = get_breach(weaponData.breach, weaponData.level)
        for i in range(0, weapon_breach):
            weapon_bg_temp.alpha_composite(promote_icon.copy(), dest=(200 + 40 * i, 100))

        weapon_bg_temp.alpha_composite(weapon_icon_bg, dest=(45, 0))

        bar_bg.alpha_composite(weapon_bg_temp.resize((260, 130)), dest=(580, 25))

        # 伤害
        bar_star_draw.text((870, 45), f'{rank.expected_damage}', SPECIAL_GOLD, waves_font_34, 'mm')
        bar_star_draw.text((870, 75), f'{damage_title}', 'white', waves_font_16, 'mm')

        # 排名
        info_block = Image.new("RGBA", (50, 50), color=(255, 255, 255, 0))
        info_block_draw = ImageDraw.Draw(info_block)
        rank_color = (54, 54, 54)
        if index == 0:
            rank_color = (255, 0, 0)
        elif index == 1:
            rank_color = (255, 180, 0)
        elif index == 2:
            rank_color = (185, 106, 217)
        info_block_draw.rounded_rectangle([0, 0, 50, 50], radius=8, fill=rank_color + (int(0.9 * 255),))

        info_block_draw.text((24, 24), f'{index + 1}', 'white', waves_font_34, 'mm')
        bar_bg.alpha_composite(info_block, (40, 30))

        # 贴到背景
        card_img.paste(bar_bg, (0, title_h + index * bar_star_h), bar_bg)

        total_score += rank.score
        total_damage += rank.expected_damage_int

    avg_score = f"{total_score / totalNum:.1f}" if totalNum != 0 else "0"
    avg_damage = f"{total_damage / totalNum:,.0f}" if totalNum != 0 else "0"

    title = TITLE_I.copy()
    title_draw = ImageDraw.Draw(title)
    # logo
    title.alpha_composite(logo_img.copy(), dest=(50, 65))

    # 人物bg
    pile = await get_role_pile(char_id)
    title.paste(pile, (450, -120), pile)
    title_draw.text((200, 335), f'{avg_score}', 'white', waves_font_44, 'mm')
    title_draw.text((200, 375), f'平均声骸分数', SPECIAL_GOLD, waves_font_20, 'mm')

    title_draw.text((390, 335), f'{avg_damage}', 'white', waves_font_44, 'mm')
    title_draw.text((390, 375), f'平均伤害', SPECIAL_GOLD, waves_font_20, 'mm')

    if char_id in special_char_name:
        char_name = special_char_name[char_id]
    title_draw.text((140, 260), f'{char_name}排行', 'black', waves_font_44, 'lm')

    img_temp = Image.new('RGBA', char_mask.size)
    img_temp.paste(title, (0, 0), char_mask.copy())
    card_img.alpha_composite(img_temp, (0, 0))
    card_img = add_footer(card_img)
    card_img = await convert_img(card_img)
    return card_img


async def get_avatar(
    ev: Event, qid: Optional[Union[int, str]], char_id: Union[int, str],
) -> Image.Image:
    if ev.bot_id == 'onebot':
        pic = await get_qq_avatar(qid)
        pic_temp = crop_center_img(pic, 120, 120)

        img = Image.new('RGBA', (180, 180))
        avatar_mask_temp = avatar_mask.copy()
        mask_pic_temp = avatar_mask_temp.resize((120, 120))
        img.paste(pic_temp, (0, -5), mask_pic_temp)
    else:
        pic = await get_square_avatar(char_id)

        pic_temp = Image.new('RGBA', pic.size)
        pic_temp.paste(pic.resize((160, 160)), (10, 10))
        pic_temp = pic_temp.resize((160, 160))

        avatar_mask_temp = avatar_mask.copy()
        mask_pic_temp = Image.new('RGBA', avatar_mask_temp.size)
        mask_pic_temp.paste(avatar_mask_temp, (-20, -45), avatar_mask_temp)
        mask_pic_temp = mask_pic_temp.resize((160, 160))

        img = Image.new('RGBA', (180, 180))
        img.paste(pic_temp, (0, 0), mask_pic_temp)

    return img


def get_weapon_icon_bg(star: int = 3) -> Image.Image:
    if star < 3:
        star = 3

    if star == 3:
        return weapon_icon_bg_3.copy()
    elif star == 4:
        return weapon_icon_bg_4.copy()
    else:
        return weapon_icon_bg_5.copy()
