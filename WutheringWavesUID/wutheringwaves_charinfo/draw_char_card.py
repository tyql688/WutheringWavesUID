import copy
import re
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_event_avatar, crop_center_img
from ..utils import hint
from ..utils.api.model import RoleDetailData, AccountBaseInfo, WeaponData
from ..utils.ascension.weapon import get_weapon_detail, WavesWeaponResult, get_breach
from ..utils.calculate import calc_phantom_score, get_total_score_bg, get_valid_color, get_calc_map
from ..utils.char_info_utils import get_all_role_detail_info
from ..utils.damage.abstract import DamageDetailRegister
from ..utils.error_reply import WAVES_CODE_102
from ..utils.expression_ctx import prepare_phantom, enhance_summation_phantom_value, enhance_summation_card_value, \
    card_sort_map_to_attribute
from ..utils.fonts.waves_fonts import waves_font_30, waves_font_25, waves_font_50, waves_font_40, waves_font_20, \
    waves_font_24, waves_font_28, waves_font_26, waves_font_42
from ..utils.image import get_waves_bg, add_footer, GOLD, get_role_pile, get_weapon_type, get_attribute, \
    get_square_weapon, get_attribute_prop, GREY, SPECIAL_GOLD, get_small_logo
from ..utils.name_convert import alias_to_char_name, char_name_to_char_id
from ..utils.resource.download_file import get_chain_img, get_phantom_img, get_fetter_img, get_skill_img
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import PREFIX

TEXT_PATH = Path(__file__).parent / 'texture2d'

ph_sort_name = [
    [
        ("生命", '0'),
        ("攻击", '0'),
        ("防御", '0'),
        ("共鸣效率", '0%')
    ],
    [
        ("暴击", '0.0%'),
        ("暴击伤害", '0.0%'),
        ("属性伤害加成", '0.0%'),
        ("治疗效果加成", '0.0%')
    ],
    [
        ("普攻伤害加成", '0.0%'),
        ("重击伤害加成", '0.0%'),
        ("共鸣技能伤害加成", '0.0%'),
        ("共鸣解放伤害加成", '0.0%')
    ]
]

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

card_sort_name = [
    ("生命", '0'),
    ("攻击", '0'),
    ("防御", '0'),
    ("共鸣效率", '0%'),
    ("暴击", '0.0%'),
    ("暴击伤害", '0.0%'),
    ("属性伤害加成", '0.0%'),
    ("治疗效果加成", '0.0%')
]

damage_bar1 = Image.open(TEXT_PATH / 'damage_bar1.png')
damage_bar2 = Image.open(TEXT_PATH / 'damage_bar2.png')


async def draw_char_detail_img(ev: Event, uid: str, char: str):
    ck = await waves_api.get_ck(uid)
    if not ck:
        return hint.error_reply(WAVES_CODE_102)
    # 账户数据
    succ, account_info = await waves_api.get_base_info(uid, ck)
    if not succ:
        return account_info
    account_info = AccountBaseInfo(**account_info)

    char_id = char_name_to_char_id(char)
    if not char_id:
        return f'[鸣潮] 角色名{char}无法找到, 可能暂未适配, 请先检查输入是否正确！'

    char_name = alias_to_char_name(char)
    all_role_detail: dict[str, RoleDetailData] = await get_all_role_detail_info(uid)

    if all_role_detail is None or char_name not in all_role_detail:
        return f'[鸣潮] 未找到该角色信息, 请先使用[{PREFIX}刷新面板]进行刷新!'

    role_detail: RoleDetailData = all_role_detail[char_name]
    damageDetail = DamageDetailRegister.find_class(char_id)
    ph_sum_value = 250
    jineng_len = 180
    dd_len = 0
    if damageDetail:
        dd_len = 60 + (len(damageDetail) + 1) * 60
    img = get_waves_bg(1200, 2650 + ph_sum_value + jineng_len + dd_len, 'bg3')

    # 头像部分
    avatar = await draw_pic_with_ring(ev)
    avatar_ring = Image.open(TEXT_PATH / 'avatar_ring.png')

    img.paste(avatar, (45, 20), avatar)
    avatar_ring = avatar_ring.resize((180, 180))
    img.paste(avatar_ring, (55, 30), avatar_ring)

    base_info_bg = Image.open(TEXT_PATH / 'base_info_bg.png')
    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text((275, 120), f'{account_info.name[:7]}', 'white', waves_font_30, 'lm')
    base_info_draw.text((226, 173), f'特征码:  {account_info.id}', GOLD, waves_font_25, 'lm')
    img.paste(base_info_bg, (35, -30), base_info_bg)

    if account_info.is_full:
        title_bar = Image.open(TEXT_PATH / 'title_bar.png')
        title_bar_draw = ImageDraw.Draw(title_bar)
        title_bar_draw.text((510, 125), '账号等级', GREY, waves_font_26, 'mm')
        title_bar_draw.text((510, 78), f'Lv.{account_info.level}', 'white', waves_font_42, 'mm')

        title_bar_draw.text((660, 125), '世界等级', GREY, waves_font_26, 'mm')
        title_bar_draw.text((660, 78), f'Lv.{account_info.worldLevel}', 'white', waves_font_42, 'mm')

        logo_img = get_small_logo(2)
        title_bar.alpha_composite(logo_img, dest=(780, 65))
        img.paste(title_bar, (200, 15), title_bar)

    # 左侧pile部分
    role_pile = await get_role_pile(role_detail.role.roleId)
    char_mask = Image.open(TEXT_PATH / 'char_mask.png')
    char_fg = Image.open(TEXT_PATH / 'char_fg.png')

    role_attribute = await get_attribute(role_detail.role.attributeName)
    role_attribute = role_attribute.resize((50, 50)).convert('RGBA')
    char_fg.paste(role_attribute, (434, 112), role_attribute)
    weapon_type = await get_weapon_type(role_detail.role.weaponTypeName)
    weapon_type = weapon_type.resize((40, 40)).convert('RGBA')
    char_fg.paste(weapon_type, (439, 182), weapon_type)

    char_fg_image = ImageDraw.Draw(char_fg)
    roleName = role_detail.role.roleName
    if "漂泊者" in roleName:
        roleName = "漂泊者"

    draw_text_with_shadow(char_fg_image,
                          f'{roleName}',
                          296, 867,
                          waves_font_50, anchor='rm')
    draw_text_with_shadow(char_fg_image,
                          f'Lv.{role_detail.role.level}',
                          300, 875,
                          waves_font_30, anchor='lm')

    role_pile_image = Image.new('RGBA', (560, 1000))
    role_pile_image.paste(role_pile, ((560 - role_pile.size[0]) // 2, (1000 - role_pile.size[1]) // 2), role_pile)
    img.paste(role_pile_image, (25, 170), char_mask)
    img.paste(char_fg, (25, 170), char_fg)

    # 右侧属性-技能
    right_image_temp = Image.new('RGBA', (600, 1100))

    # 武器banner
    banner2 = Image.open(TEXT_PATH / 'banner2.png')
    right_image_temp.alpha_composite(banner2, dest=(0, 550))

    # 右侧属性-武器
    weapon_bg = Image.open(TEXT_PATH / 'weapon_bg.png')
    weapon_bg_temp = Image.new('RGBA', weapon_bg.size)
    weapon_bg_temp.alpha_composite(weapon_bg, dest=(0, 0))

    weaponData: WeaponData = role_detail.weaponData

    weapon_icon = await get_square_weapon(weaponData.weapon.weaponId)
    weapon_icon = crop_center_img(weapon_icon, 110, 110)
    weapon_icon_bg = get_weapon_icon_bg(weaponData.weapon.weaponStarLevel)
    weapon_icon_bg.paste(weapon_icon, (10, 20), weapon_icon)

    weapon_bg_temp_draw = ImageDraw.Draw(weapon_bg_temp)
    weapon_bg_temp_draw.text((200, 30), f'{weaponData.weapon.weaponName}', SPECIAL_GOLD, waves_font_40, 'lm')
    weapon_bg_temp_draw.text((203, 75), f'Lv.{weaponData.level}/90', 'white', waves_font_30, 'lm')

    _x = 220 + 43 * len(weaponData.weapon.weaponName)
    _y = 37
    weapon_bg_temp_draw.rounded_rectangle([_x - 15, _y - 15, _x + 50, _y + 15], radius=7,
                                          fill=(128, 138, 135, int(0.8 * 255)))
    weapon_bg_temp_draw.text((_x, _y), f'精{weaponData.resonLevel}', 'white',
                             waves_font_24, 'lm')

    weapon_breach = get_breach(weaponData.breach, weaponData.level)
    for i in range(0, weapon_breach):
        promote_icon = Image.open(TEXT_PATH / 'promote_icon.png')
        weapon_bg_temp.alpha_composite(promote_icon, dest=(200 + 40 * i, 100))

    weapon_bg_temp.alpha_composite(weapon_icon_bg, dest=(45, 0))

    weapon_detail: WavesWeaponResult = get_weapon_detail(
        weaponData.weapon.weaponId,
        weaponData.level,
        weaponData.breach,
        weaponData.resonLevel)
    stats_main = await get_attribute_prop(weapon_detail.stats[0]['name'])
    stats_main = stats_main.resize((40, 40))
    weapon_bg_temp.alpha_composite(stats_main, (65, 187))
    weapon_bg_temp_draw.text((130, 207), f'{weapon_detail.stats[0]["name"]}', 'white', waves_font_30, 'lm')
    weapon_bg_temp_draw.text((500, 207), f'{weapon_detail.stats[0]["value"]}', 'white', waves_font_30, 'rm')
    stats_sub = await get_attribute_prop(weapon_detail.stats[1]['name'])
    stats_sub = stats_sub.resize((40, 40))
    weapon_bg_temp.alpha_composite(stats_sub, (65, 237))
    weapon_bg_temp_draw.text((130, 257), f'{weapon_detail.stats[1]["name"]}', 'white', waves_font_30, 'lm')
    weapon_bg_temp_draw.text((500, 257), f'{weapon_detail.stats[1]["value"]}', 'white', waves_font_30, 'rm')

    right_image_temp.alpha_composite(weapon_bg_temp, dest=(0, 650))

    # 命座部分
    mz_temp = Image.new('RGBA', (1200, 300))

    for i, _mz in enumerate(role_detail.chainList):
        mz_bg = Image.open(TEXT_PATH / 'mz_bg.png')
        mz_bg_temp = Image.new('RGBA', mz_bg.size)
        mz_bg_temp_draw = ImageDraw.Draw(mz_bg_temp)
        chain = await get_chain_img(role_detail.role.roleId, _mz.order, _mz.iconUrl)
        chain = chain.resize((100, 100))
        mz_bg.paste(chain, (95, 75), chain)
        mz_bg_temp.alpha_composite(mz_bg, dest=(0, 0))

        name = re.sub(r'[",，]+', '', _mz.name)
        mz_bg_temp_draw.text((147, 230), f'{name}', 'white', waves_font_20, 'mm')

        if not _mz.unlocked:
            mz_bg_temp = ImageEnhance.Brightness(mz_bg_temp).enhance(0.5)
        mz_temp.alpha_composite(mz_bg_temp, dest=(i * 190, 0))

    img.paste(mz_temp, (0, 1080 + jineng_len), mz_temp)

    # 声骸
    phantom_temp = Image.new('RGBA', (1200, 1280 + ph_sum_value))
    banner3 = Image.open(TEXT_PATH / 'banner3.png')
    phantom_temp.alpha_composite(banner3, dest=(0, 0))

    ph_0 = Image.open(TEXT_PATH / 'ph_0.png')
    ph_1 = Image.open(TEXT_PATH / 'ph_1.png')
    phantom_sum_value = {}
    if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
        totalCost = role_detail.phantomData.cost
        equipPhantomList = role_detail.phantomData.equipPhantomList
        phantom_score = 0

        phantom_sum_value = prepare_phantom(equipPhantomList)
        phantom_sum_value = enhance_summation_phantom_value(
            char_id, role_detail.role.level, role_detail.role.breach,
            weaponData.weapon.weaponId, weaponData.level, weaponData.breach, weaponData.resonLevel,
            phantom_sum_value)
        calc_temp = get_calc_map(phantom_sum_value, role_detail.role.roleName)
        for i, _phantom in enumerate(equipPhantomList):
            sh_temp = Image.new('RGBA', (350, 550))
            sh_temp_draw = ImageDraw.Draw(sh_temp)
            sh_bg = Image.open(TEXT_PATH / 'sh_bg.png')
            sh_temp.alpha_composite(sh_bg, dest=(0, 0))
            if _phantom and _phantom.phantomProp:
                props = []
                if _phantom.mainProps:
                    props.extend(_phantom.mainProps)
                if _phantom.subProps:
                    props.extend(_phantom.subProps)
                _score, _bg = calc_phantom_score(char_name, props, _phantom.cost, calc_temp)

                phantom_score += _score
                sh_title = Image.open(TEXT_PATH / f'sh_title_{_bg}.png')

                sh_temp.alpha_composite(sh_title, dest=(0, 0))

                phantom_icon = await get_phantom_img(_phantom.phantomProp.phantomId, _phantom.phantomProp.iconUrl)
                fetter_icon = await get_fetter_img(_phantom.fetterDetail.name, _phantom.fetterDetail.iconUrl)
                phantom_icon.alpha_composite(fetter_icon, dest=(210, 0))
                phantom_icon = phantom_icon.resize((100, 100))
                sh_temp.alpha_composite(phantom_icon, dest=(20, 20))
                phantomName = _phantom.phantomProp.name.replace("·", " ").replace("（", " ").replace("）", "")
                sh_temp_draw.text((130, 40), f'{phantomName}', SPECIAL_GOLD, waves_font_28, 'lm')

                # 声骸等级背景
                ph_level_img = Image.new('RGBA', (84, 30), (255, 255, 255, 0))
                ph_level_img_draw = ImageDraw.Draw(ph_level_img)
                ph_level_img_draw.rounded_rectangle([0, 0, 84, 30], radius=8, fill=(0, 0, 0, int(0.8 * 255)))
                ph_level_img_draw.text((8, 13), f'Lv.{_phantom.level}', 'white', waves_font_24, 'lm')
                sh_temp.alpha_composite(ph_level_img, (128, 58))

                # 声骸分数背景
                ph_score_img = Image.new('RGBA', (92, 30), (255, 255, 255, 0))
                ph_score_img_draw = ImageDraw.Draw(ph_score_img)
                ph_score_img_draw.rounded_rectangle([0, 0, 92, 30], radius=8, fill=(186, 55, 42, int(0.8 * 255)))
                ph_score_img_draw.text((5, 13), f'{_score}分', 'white', waves_font_24, 'lm')
                sh_temp.alpha_composite(ph_score_img, (228, 58))

                # sh_temp_draw.text((142, 70), f'Lv.{_phantom.level}', 'white', waves_font_24, 'lm')
                # sh_temp_draw.text((242, 70), f'{_score}分', 'white', waves_font_24, 'lm')
                for index in range(0, _phantom.cost):
                    promote_icon = Image.open(TEXT_PATH / 'promote_icon.png')
                    promote_icon = promote_icon.resize((30, 30))
                    sh_temp.alpha_composite(promote_icon, dest=(128 + 30 * index, 90))

                for index, _prop in enumerate(props):
                    oset = 55
                    prop_img = await get_attribute_prop(_prop.attributeName)
                    prop_img = prop_img.resize((40, 40))
                    sh_temp.alpha_composite(prop_img, (15, 167 + index * oset))
                    sh_temp_draw = ImageDraw.Draw(sh_temp)
                    name_color = 'white'
                    num_color = 'white'
                    if index > 1:
                        name_color, num_color = get_valid_color(_prop.attributeName, _prop.attributeValue, calc_temp)
                    sh_temp_draw.text((60, 187 + index * oset), f'{_prop.attributeName[:6]}', name_color, waves_font_24,
                                      'lm')
                    sh_temp_draw.text((343, 187 + index * oset), f'{_prop.attributeValue}', num_color, waves_font_24,
                                      'rm')

            phantom_temp.alpha_composite(
                sh_temp,
                dest=(40 + ((i + 1) % 3) * 380, 120 + ph_sum_value + ((i + 1) // 3) * 600))

        if phantom_score > 0:
            _bg = get_total_score_bg(char_name, phantom_score, calc_temp)
            sh_score_bg_c = Image.open(TEXT_PATH / f'sh_score_bg_{_bg}.png')
            score_temp = Image.new('RGBA', sh_score_bg_c.size)
            score_temp.alpha_composite(sh_score_bg_c)
            sh_score_c = Image.open(TEXT_PATH / f'sh_score_{_bg}.png')
            score_temp.alpha_composite(sh_score_c)
            score_temp_draw = ImageDraw.Draw(score_temp)

            score_temp_draw.text((180, 260), f'声骸评级', GREY, waves_font_40, 'mm')
            score_temp_draw.text((180, 380), f'{phantom_score:.2f}分', 'white', waves_font_40, 'mm')
            score_temp_draw.text((180, 440), f'声骸评分', GREY, waves_font_40, 'mm')
        else:
            abs_bg = Image.open(TEXT_PATH / f'abs.png')
            score_temp = Image.new('RGBA', abs_bg.size)
            score_temp.alpha_composite(abs_bg)
            score_temp_draw = ImageDraw.Draw(score_temp)
            score_temp_draw.text((180, 130), f'暂无', 'white', waves_font_40, 'mm')
            score_temp_draw.text((180, 380), f'- 分', 'white', waves_font_40, 'mm')

        phantom_temp.alpha_composite(score_temp, dest=(40, 120 + ph_sum_value))

        shuxing = f"{role_detail.role.attributeName}伤害加成"
        for mi, m in enumerate(ph_sort_name):
            for ni, name_default in enumerate(m):
                name, default_value = name_default
                if name == "属性伤害加成":
                    value = phantom_sum_value.get(shuxing, default_value)
                    prop_img = await get_attribute_prop(shuxing)
                    name_color, _ = get_valid_color(shuxing, value, calc_temp)
                    name = shuxing
                else:
                    value = phantom_sum_value.get(name, default_value)
                    prop_img = await get_attribute_prop(name)
                    name_color, _ = get_valid_color(name, value, calc_temp)
                prop_img = prop_img.resize((40, 40))
                ph_bg = ph_0.copy() if ni % 2 == 0 else ph_1.copy()
                ph_bg.alpha_composite(prop_img, (20, 32))
                ph_bg_draw = ImageDraw.Draw(ph_bg)

                ph_bg_draw.text((70, 50), f'{name[:6]}', name_color, waves_font_24,
                                'lm')
                ph_bg_draw.text((343, 50), f'{value}', name_color, waves_font_24,
                                'rm')

                phantom_temp.alpha_composite(ph_bg, (40 + mi * 370, 100 + ni * 50))

        ph_tips = ph_1.copy()
        ph_tips_draw = ImageDraw.Draw(ph_tips)
        ph_tips_draw.text((20, 50), f'[提示]评分模板', 'white', waves_font_24, 'lm')
        ph_tips_draw.text((350, 50), f'{calc_temp["name"]}', (255, 255, 0), waves_font_24, 'rm')
        # phantom_temp.alpha_composite(ph_tips, (40 + 2 * 370, 100 + 4 * 50))
        phantom_temp.alpha_composite(ph_tips, (40 + 2 * 370, 45))

    img.paste(phantom_temp, (0, 1320 + jineng_len), phantom_temp)

    # 面板
    card_map = enhance_summation_card_value(char_id, role_detail.role.level, role_detail.role.breach,
                                            role_detail.role.attributeName,
                                            weaponData.weapon.weaponId, weaponData.level, weaponData.breach,
                                            weaponData.resonLevel,
                                            phantom_sum_value, card_sort_map)
    calc_temp = get_calc_map(card_map, role_detail.role.roleName)

    if damageDetail:
        damageAttribute = card_sort_map_to_attribute(card_map)
        damage_title_bg = damage_bar1.copy()
        damage_title_bg_draw = ImageDraw.Draw(damage_title_bg)
        damage_title_bg_draw.text((400, 50), f'伤害类型', 'white', waves_font_24, 'rm')
        damage_title_bg_draw.text((700, 50), f'暴击伤害', 'white', waves_font_24, 'mm')
        damage_title_bg_draw.text((1000, 50), f'期望伤害', 'white', waves_font_24, 'mm')
        img.alpha_composite(damage_title_bg, dest=(0, 2600 + ph_sum_value + jineng_len))
        for dindex, damage_temp in enumerate(damageDetail):
            damage_title = damage_temp['title']
            damageAttributeTemp = copy.deepcopy(damageAttribute)
            crit_damage, expected_damage = damage_temp['func'](damageAttributeTemp, role_detail)
            # logger.debug(f"{char_name}-{damage_title} 暴击伤害: {crit_damage}")
            # logger.debug(f"{char_name}-{damage_title} 期望伤害: {expected_damage}")
            # logger.debug(f"{char_name}-{damage_title} 属性值: {damageAttributeTemp}")

            damage_bar = damage_bar2.copy() if dindex % 2 == 0 else damage_bar1.copy()
            damage_bar_draw = ImageDraw.Draw(damage_bar)
            damage_bar_draw.text((400, 50), f'{damage_title}', 'white', waves_font_24, 'rm')
            damage_bar_draw.text((700, 50), f'{crit_damage}', 'white', waves_font_24, 'mm')
            damage_bar_draw.text((1000, 50), f'{expected_damage}', 'white', waves_font_24, 'mm')
            img.alpha_composite(damage_bar, dest=(0, 2600 + ph_sum_value + jineng_len + (dindex + 1) * 60))

    banner1 = Image.open(TEXT_PATH / 'banner4.png')
    right_image_temp.alpha_composite(banner1, dest=(0, 0))
    sh_bg = Image.open(TEXT_PATH / 'prop_bg.png')
    sh_bg_draw = ImageDraw.Draw(sh_bg)

    shuxing = f"{role_detail.role.attributeName}伤害加成"
    for index, name_default in enumerate(card_sort_name):
        name, default_value = name_default
        if name == "属性伤害加成":
            value = card_map.get(shuxing, default_value)
            prop_img = await get_attribute_prop(shuxing)
            name_color, _ = get_valid_color(shuxing, value, calc_temp)
            name = shuxing
        else:
            value = card_map.get(name, default_value)
            prop_img = await get_attribute_prop(name)
            name_color, _ = get_valid_color(name, value, calc_temp)

        prop_img = prop_img.resize((40, 40))
        sh_bg.alpha_composite(prop_img, (60, 40 + index * 55))
        sh_bg_draw.text((120, 58 + index * 55), f'{name[:6]}', name_color, waves_font_24,
                        'lm')
        sh_bg_draw.text((530, 58 + index * 55), f'{value}', name_color, waves_font_24,
                        'rm')

    right_image_temp.alpha_composite(sh_bg, dest=(0, 80))
    img.paste(right_image_temp, (570, 200), right_image_temp)

    # 技能
    skill_bar = Image.open(TEXT_PATH / 'skill_bar.png')
    skill_bg_1 = Image.open(TEXT_PATH / 'skill_bg.png')

    temp_i = 0
    for _, _skill in enumerate(role_detail.skillList):
        if _skill.skill.type == '延奏技能':
            continue
        skill_bg = skill_bg_1.copy()

        skill_img = await get_skill_img(role_detail.role.roleId, _skill.skill.name, _skill.skill.iconUrl)
        skill_img = skill_img.resize((70, 70))
        skill_bg.paste(skill_img, (57, 65), skill_img)

        skill_bg_draw = ImageDraw.Draw(skill_bg)
        skill_bg_draw.text((150, 83), f'{_skill.skill.type}', 'white', waves_font_25, 'lm')
        skill_bg_draw.text((150, 113), f'Lv.{_skill.level}', 'white', waves_font_25, 'lm')

        skill_bg_temp = Image.new('RGBA', skill_bg.size)
        skill_bg_temp = Image.alpha_composite(skill_bg_temp, skill_bg)

        _x = 20 + temp_i * 215
        _y = -20
        skill_bar.alpha_composite(skill_bg_temp, dest=(_x, _y))
        temp_i += 1
    img.alpha_composite(skill_bar, dest=(0, 1150))

    img = add_footer(img)
    img = await convert_img(img)
    return img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev)

    mask_pic = Image.open(TEXT_PATH / 'avatar_mask.png')
    img = Image.new('RGBA', (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img


def draw_text_with_shadow(
    image: ImageDraw,
    text: str,
    _x: int, _y: int,
    font: ImageFont,
    fill_color: str = "white",
    shadow_color: str = "black",
    offset: Tuple[int, int] = (2, 2),
    anchor='rm'
):
    """描边"""
    for i in range(-offset[0], offset[0] + 1):
        for j in range(-offset[1], offset[1] + 1):
            image.text((_x + i, _y + j), text, font=font, fill=shadow_color, anchor=anchor)

    image.text((_x, _y), text, font=font, fill=fill_color, anchor=anchor)


def get_weapon_icon_bg(star: int = 3) -> Image.Image:
    if star < 3:
        star = 3
    bg_path = TEXT_PATH / f'weapon_icon_bg_{star}.png'
    bg_img = Image.open(bg_path)
    return bg_img
