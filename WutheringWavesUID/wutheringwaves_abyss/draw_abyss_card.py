from pathlib import Path
from typing import Union, Optional

from PIL import Image, ImageDraw

from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_event_avatar, crop_center_img
from ..utils.api.model import AccountBaseInfo, AbyssChallenge, RoleList, RoleDetailData, AbyssFloor
from ..utils.char_info_utils import get_all_role_detail_info
from ..utils.error_reply import WAVES_CODE_102, WAVES_CODE_999
from ..utils.fonts.waves_fonts import waves_font_30, waves_font_25, waves_font_26, waves_font_42, waves_font_32, \
    waves_font_18, waves_font_40, waves_font_36
from ..utils.hint import error_reply
from ..utils.image import get_waves_bg, add_footer, GOLD, GREY, get_square_avatar
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / 'texture2d'

ABYSS_ERROR_MESSAGE_NO_DATA = "当前暂无深渊数据"
ABYSS_ERROR_MESSAGE_NO_UNLOCK = "深渊暂未解锁"
ABYSS_ERROR_MESSAGE_NO_DEEP = "当前暂无深境区深渊数据"


async def get_abyss_data(uid: str, ck: str, is_self_ck: bool):
    if is_self_ck:
        abyss_data = await waves_api.get_abyss_data(uid, ck)
    else:
        abyss_data = await waves_api.get_abyss_index(uid, ck)

    if abyss_data.get('code') == 200:
        if not abyss_data.get('data') or not abyss_data['data'].get("isUnlock", False):
            return ABYSS_ERROR_MESSAGE_NO_DATA
        else:
            return AbyssChallenge(**abyss_data['data'])
    else:
        msg = error_reply(WAVES_CODE_999)
        if abyss_data.get('msg'):
            msg = abyss_data['msg']
        return error_reply(msg=msg)


async def draw_abyss_img(
    ev: Event,
    uid: str,
    floor: Optional[int] = None,
    schedule_type: str = '1',
) -> Union[bytes, str]:
    is_self_ck, ck = await waves_api.get_ck_result(uid)
    if not ck:
        return error_reply(WAVES_CODE_102)

    # succ, game_info = await waves_api.get_game_role_info(ck)
    # if not succ:
    #     return game_info
    # game_info = KuroRoleInfo(**game_info)

    text = ev.text.strip()
    difficultyName = "深境区"
    if "超载" in text:
        difficultyName = '超载区'
    elif "稳定" in text:
        difficultyName = '稳定区'
    elif "实验" in text:
        difficultyName = '实验区'

    # 账户数据
    succ, account_info = await waves_api.get_base_info(uid, ck)
    if not succ:
        return account_info
    account_info = AccountBaseInfo(**account_info)

    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(uid, ck)
    if not succ:
        return role_info
    role_info = RoleList(**role_info)

    # 深渊
    abyss_data = await get_abyss_data(uid, ck, is_self_ck)
    if isinstance(abyss_data, str):
        return abyss_data
    if not abyss_data.isUnlock:
        return ABYSS_ERROR_MESSAGE_NO_UNLOCK

    abyss_check = next((abyss for abyss in abyss_data.difficultyList if abyss.difficultyName == '深境区'), None)
    if not abyss_check:
        return ABYSS_ERROR_MESSAGE_NO_DEEP

    if is_self_ck:
        h = 2200
    else:
        h = 1300
    card_img = get_waves_bg(950, h, 'bg4')

    # 基础信息 名字 特征码
    base_info_bg = Image.open(TEXT_PATH / 'base_info_bg.png')
    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text((275, 120), f'{account_info.name[:7]}', 'white', waves_font_30, 'lm')
    base_info_draw.text((226, 173), f'特征码:  {account_info.id}', GOLD, waves_font_25, 'lm')
    card_img.paste(base_info_bg, (15, 20), base_info_bg)

    # 头像 头像环
    avatar = await draw_pic_with_ring(ev)
    avatar_ring = Image.open(TEXT_PATH / 'avatar_ring.png')
    card_img.paste(avatar, (25, 70), avatar)
    avatar_ring = avatar_ring.resize((180, 180))
    card_img.paste(avatar_ring, (35, 80), avatar_ring)

    # 账号基本信息，由于可能会没有，放在一起
    if account_info.is_full:
        title_bar = Image.open(TEXT_PATH / 'title_bar.png')
        title_bar_draw = ImageDraw.Draw(title_bar)
        title_bar_draw.text((660, 125), '账号等级', GREY, waves_font_26, 'mm')
        title_bar_draw.text((660, 78), f'Lv.{account_info.level}', 'white', waves_font_42, 'mm')

        title_bar_draw.text((810, 125), '世界等级', GREY, waves_font_26, 'mm')
        title_bar_draw.text((810, 78), f'Lv.{account_info.worldLevel}', 'white', waves_font_42, 'mm')
        card_img.paste(title_bar, (-20, 70), title_bar)

    # 根据面板数据获取详细信息
    role_detail_info_map = await get_all_role_detail_info(uid)

    # frame
    frame = Image.open(TEXT_PATH / 'frame.png')
    frame = frame.resize((frame.size[0], h - 50 if is_self_ck else h - 100), box=(0, 0, frame.size[0], h))

    yset = 0
    for _abyss in abyss_data.difficultyList:
        if _abyss.difficultyName != difficultyName:
            continue
        for tower_index, tower in enumerate(_abyss.towerAreaList):
            tower_name_bg = Image.open(TEXT_PATH / f'tower_name_bg{tower.areaId}.png')
            tower_name_bg_draw = ImageDraw.Draw(tower_name_bg)
            tower_name_bg_draw.text((170, 50), f'{difficultyName}-{tower.areaName}', 'white', waves_font_36, 'lm')
            if is_self_ck:
                tower_name_bg_draw.text((500, 60), f'{tower.star}/{tower.maxStar}', 'white', waves_font_32, 'mm')
            frame.paste(tower_name_bg, (-20, 300 + yset), tower_name_bg)

            yset += 150
            if not tower.floorList:
                tower.floorList = [AbyssFloor(**{"floor": 1, "picUrl": "", "star": 0, "roleList": None})]
            for floor_index, floor in enumerate(tower.floorList):
                abyss_bg = Image.open(TEXT_PATH / f'abyss_bg_{floor.floor}.jpg').convert('RGBA')
                abyss_bg = abyss_bg.resize((abyss_bg.size[0] + 100, abyss_bg.size[1]))
                abyss_bg_temp = Image.new('RGBA', abyss_bg.size)
                name_bg = Image.open(TEXT_PATH / f'name_bg.png')
                name_bg_draw = ImageDraw.Draw(name_bg)
                if floor.floor == 1:
                    _floor = '一'
                elif floor.floor == 2:
                    _floor = '二'
                elif floor.floor == 3:
                    _floor = '三'
                elif floor.floor == 4:
                    _floor = '四'
                name_bg_draw.text((70, 50), f'第{_floor}层', 'white', waves_font_40, 'lm')
                abyss_bg_temp.paste(name_bg, (0, 0), name_bg)

                # 星数
                for i in range(3):
                    if i + 1 <= floor.star:
                        star_bg = Image.open(TEXT_PATH / f'star_full.png')
                    else:
                        star_bg = Image.open(TEXT_PATH / f'star_empty.png')
                    abyss_bg_temp.paste(star_bg, (10 + i * 70, 50), star_bg)

                if floor.roleList:
                    for role_index, _role in enumerate(floor.roleList):
                        role = next((role for role in role_info.roleList if role.roleId == _role.roleId), None)

                        avatar = await draw_pic(role.roleId)
                        char_bg = Image.open(TEXT_PATH / f'char_bg{role.starLevel}.png')
                        char_bg_draw = ImageDraw.Draw(char_bg)
                        char_bg_draw.text((90, 150), f'{role.roleName}', 'white', waves_font_18, 'mm')
                        char_bg.paste(avatar, (0, 0), avatar)
                        if role_detail_info_map and role.roleName in role_detail_info_map:
                            temp: RoleDetailData = role_detail_info_map[role.roleName]
                            info_block = Image.new("RGBA", (40, 20), color=(255, 255, 255, 0))
                            info_block_draw = ImageDraw.Draw(info_block)
                            info_block_draw.rectangle([0, 0, 40, 20], fill=(96, 12, 120, int(0.9 * 255)))
                            info_block_draw.text((2, 10), f'{temp.get_chain_name()}', 'white', waves_font_18, 'lm')
                            char_bg.paste(info_block, (110, 35), info_block)

                        abyss_bg_temp.alpha_composite(char_bg, (300 + role_index * 150, -20))

                abyss_bg.paste(abyss_bg_temp, (0, 0), abyss_bg_temp)
                frame.paste(abyss_bg, (80, 240 + yset), abyss_bg)
                yset += 141
        break
    else:
        return ABYSS_ERROR_MESSAGE_NO_DATA

    card_img.paste(frame, (0, 0), frame)

    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev)

    mask_pic = Image.open(TEXT_PATH / 'avatar_mask.png')
    img = Image.new('RGBA', (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img


async def draw_pic(roleId):
    pic = await get_square_avatar(roleId)
    mask_pic = Image.open(TEXT_PATH / 'avatar_mask.png')
    img = Image.new('RGBA', (180, 180))
    mask = mask_pic.resize((140, 140))
    resize_pic = crop_center_img(pic, 140, 140)
    img.paste(resize_pic, (22, 18), mask)

    return img
