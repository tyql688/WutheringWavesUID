import copy
from typing import Dict
from itertools import zip_longest

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..wutheringwaves_charinfo.draw_char_card import generate_online_role_detail
from ..utils.refresh_char_detail import save_card_info
from ..utils.name_convert import (
    alias_to_char_name,
    char_name_to_char_id,
    weapon_name_to_weapon_id
)
from ..wutheringwaves_config import PREFIX
from .char_fetterDetail import get_fetterDetail_from_sonata


async def save_card_dict_to_json(bot: Bot, ev: Event, result_dict: Dict):

    at_sender = True if ev.group_id else False

    uid = result_dict["用户信息"]["UID"]

    chain_num = result_dict["角色信息"]["共鸣链"]
    
    char = result_dict["角色信息"]["角色名"]
    char_name = alias_to_char_name(char)
    char_id = char_name_to_char_id(char_name)

    if char_id is None:
        await bot.send(f"[鸣潮]识别结果为角色'{char_name}'不存在")
        logger.debug(f" [鸣潮][dc卡片识别] 用户{uid}的{char_name}识别错误！")
        return


    weapon_id = weapon_name_to_weapon_id(result_dict["武器信息"]["武器名"])

    # char_id = "1506" # 菲比..utils\map\detail_json\char\1506.json
    result = await generate_online_role_detail(char_id)
    waves_data = []
    data = {}

    # 处理 `chainList` 的数据
    data["chainList"] = []
    for chain in result.chainList:
        if chain.order <= chain_num:
            chain.unlocked = True
        data["chainList"].append({
            "name": chain.name,
            "order": chain.order,
            "description": chain.description,
            "iconUrl": chain.iconUrl,
            "unlocked": chain.unlocked
        })
        
    # 处理 `level` 的数据
    data["level"] = result_dict["角色信息"]["等级"]
        
    # 处理 `phantomData` 的数据
    if result.phantomData is not None:
        phantom_data = result.phantomData
        data["phantomData"] = {
            "cost": 12,
            "equipPhantomList": []
        }
        first_echo_id, ECHO = await get_fetterDetail_from_sonata(char_name)
        get_first_echo = True 
        for echo_value in result_dict["装备数据"]:
            # 创建 ECHO 的独立副本
            echo = copy.deepcopy(ECHO)
            # 替换第一声骸位为对应套装4C
            if get_first_echo:
                echo["phantomProp"]["phantomId"] = first_echo_id
                get_first_echo = False

            # 更新 echo 的 mainProps 和 subProps, 防止空表
            echo["mainProps"] = echo_value.get("mainProps", [])
            echo["subProps"] = echo_value.get("subProps", [])

            # 将更新后的 echo 添加到 equipPhantomList
            data["phantomData"]["equipPhantomList"].append(echo)
    
    # 处理 `role` 的数据
    if result.role is not None:
        role = result.role
        data["role"] = {
            "acronym": role.acronym,
            "attributeId": role.attributeId,
            "attributeName": role.attributeName,
            "breach": get_breach(result_dict["角色信息"]["等级"]),
            "isMainRole": False,  # 假设需要一个主角色标识（用户没有提供，可以设置默认值或动态获取）
            "level": result_dict["角色信息"]["等级"],
            "roleIconUrl": role.roleIconUrl,
            "roleId": role.roleId,
            "roleName": role.roleName,
            "rolePicUrl": role.rolePicUrl,
            "starLevel": role.starLevel,
            "weaponTypeId": role.weaponTypeId,
            "weaponTypeName": role.weaponTypeName
        }
        
    # 处理 `skillList` 的数据
    data["skillList"] = []
    # 使用 zip_longest 组合两个列表，较短的列表用默认值填充
    for skill_data, ocr_level in zip_longest(result.skillList, result_dict["技能等级"], fillvalue=1):
        skill = skill_data.skill
        data["skillList"].append({
            "level": ocr_level,
            "skill": {
                "description": skill.description,
                "iconUrl": skill.iconUrl,
                "id": skill.id,
                "name": skill.name,
                "type": skill.type
            }
        })
        
    # 处理 `weaponData` 的数据，暂时没办法处理识别到的武器名
    if result.weaponData is not None:
        weapon_data = result.weaponData
        data["weaponData"] = {
            "breach": weapon_data.breach,
            "level": weapon_data.level,
            "resonLevel": weapon_data.resonLevel,
            "weapon": {
                "weaponEffectName": weapon_data.weapon.weaponEffectName,
                "weaponIcon": weapon_data.weapon.weaponIcon,
                "weaponId": weapon_data.weapon.weaponId,
                "weaponName": weapon_data.weapon.weaponName,
                "weaponStarLevel": weapon_data.weapon.weaponStarLevel,
                "weaponType": weapon_data.weapon.weaponType
            }
        }
        if weapon_id is not None:
            data["weaponData"]["level"] = result_dict["武器信息"]["等级"]
            data["weaponData"]["breach"] = get_breach(result_dict["武器信息"]["等级"])
            data["weaponData"]["weapon"]["weaponName"] = result_dict["武器信息"]["武器名"]
            data["weaponData"]["weapon"]["weaponId"] = weapon_id

            # weapon_detail: WavesWeaponResult = get_weapon_detail(
            #     weapon_id, result_dict["武器信息"]["等级"]
            # )
            # print(weapon_detail)

    waves_data.append(data)
    await save_card_info(uid, waves_data)
    await bot.send(f"[鸣潮]dc卡片数据提取成功！\n请使用'{PREFIX}绑定{uid}'绑定您的角色\n可使用'{PREFIX}{char_name}面板'查看您的角色面板\n使用'{PREFIX}{char_name}排行'查看角色排行榜\n使用'{PREFIX}替换帮助'查看面板数据更换方法", at_sender)
    logger.info(f" [鸣潮][dc卡片识别] 数据识别完毕，用户{uid}的{char_name}面板数据已保存到本地！")

def get_breach(level: int):
    if level <= 20:
        breach = 0
    elif level <= 40:
        breach = 1
    elif level <= 50:
        breach = 2
    elif level <= 60:
        breach = 3
    elif level <= 70:
        breach = 4
    elif level <= 80:
        breach = 5
    elif level <= 90:
        breach = 6
    else:
        breach = 0
    return breach
