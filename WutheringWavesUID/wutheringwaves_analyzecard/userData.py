import re
import copy
import asyncio
from typing import Dict
from pathlib import Path
from itertools import zip_longest

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..wutheringwaves_charinfo.draw_char_card import generate_online_role_detail
from ..utils.ascension.weapon import get_weapon_detail
from ..utils.refresh_char_detail import save_card_info
from ..utils.api.model import RoleDetailData
from ..utils.calc import WuWaCalc
from ..utils.name_convert import (
    char_id_to_char_name,
    alias_to_weapon_name,
    weapon_name_to_weapon_id,
    phantom_id_to_phantom_name
)

from ..wutheringwaves_config import PREFIX
from .char_fetterDetail import get_fetterDetail_from_char, echo_data_to_cost


async def save_card_dict_to_json(bot: Bot, ev: Event, result_dict: Dict):

    at_sender = True if ev.group_id else False

    try:
        uid = result_dict["用户信息"]["UID"]

        chain_num = result_dict["角色信息"]["共鸣链"]

        char_level = result_dict["角色信息"]["等级"]
        
        char_id = result_dict["角色信息"]["角色ID"]
        char_name = char_id_to_char_name(char_id)
        char_name_print = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9\s]', '', char_name) # 删除"漂泊者·衍射"的符号

        if char_id is None:
            await bot.send(f"[鸣潮]识别结果为角色'{char_name_print}'不存在")
            logger.error(f" [鸣潮][dc卡片识别] 用户{uid}的{char_name_print}识别错误！")
            return
        weapon_name = alias_to_weapon_name(result_dict["武器信息"]["武器名"])
        weapon_id = weapon_name_to_weapon_id(result_dict["武器信息"]["武器名"])

        wepon_level = result_dict["武器信息"]["等级"]

    except Exception as e:
        logger.error(f" [鸣潮][dc卡片识别] 识别结果结构错误：{e}")
        await bot.send("[鸣潮]识别结果结构错误", at_sender)
        return


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
    data["level"] = char_level
        
    # 处理 `phantomData` 的数据
    data["phantomData"] = {
        "cost": 12,
        "equipPhantomList": []
    }

    cost_sum = 0 # 默认cost总数
    cost4_counter = 0 # 4cost 的计数器
    echo_num = len(result_dict["装备数据"])
    ECHO = await get_fetterDetail_from_char(char_id)

    for echo_value in result_dict["装备数据"]:
        # 创建 ECHO 的独立副本
        echo = copy.deepcopy(ECHO)

        echo["fetterDetail"]["num"] = echo_num
        # 更新 echo 的 mainProps 和 subProps, 防止空表
        echo["mainProps"] = echo_value.get("mainProps", [])
        echo["subProps"] = echo_value.get("subProps", [])

        # 根据主词条判断声骸cost并适配id
        echo_id, cost = await echo_data_to_cost(char_id, echo["mainProps"][0], cost4_counter)
        cost_sum += cost

        echo["phantomProp"]["name"] = f"识别默认{cost}c"
        if cost == 4:
            cost4_counter += 1  # 只有实际生成cost4时递增
            echo["phantomProp"]["name"] = phantom_id_to_phantom_name(echo_id)

        echo["phantomProp"]["phantomId"] = echo_id
        echo["phantomProp"]["cost"] = cost
        echo["cost"] = cost

        # 将更新后的 echo 添加到 equipPhantomList
        data["phantomData"]["equipPhantomList"].append(echo)
        
    data["phantomData"]["cost"] = cost_sum # 更新总cost
    
    # 处理 `role` 的数据
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
        # breach 突破、resonLevel 精炼
        data["weaponData"]["level"] = wepon_level
        data["weaponData"]["breach"] = get_breach(wepon_level)
        data["weaponData"]["weapon"]["weaponName"] = weapon_name
        data["weaponData"]["weapon"]["weaponId"] = weapon_id
        weapon_detail = get_weapon_detail(weapon_id, wepon_level)
        data["weaponData"]["weapon"]["weaponStarLevel"] = weapon_detail.starLevel

    # 检查声骸数据是否异常
    if not await check_phantom_data(data):
        await bot.send("[鸣潮]dc卡片识别数据异常！\n或请使用更高分辨率卡片重新识别！", at_sender)
        return

    waves_data.append(data)
    await save_card_info(uid, waves_data)
    await bot.send(f"[鸣潮]dc卡片数据提取成功！识别套装使用默认配置(影响伤害计算不影响声骸评分)\n可使用：\n【{PREFIX}{char_name_print}面板】查看您的角色面板\n【{PREFIX}改{char_name_print}套装**(套装名)】修改声骸套装\n【{PREFIX}改{char_name_print}声骸】修改当前套装的首位声骸\n", at_sender)
    logger.info(f" [鸣潮][dc卡片识别] 数据识别完毕，用户{uid}的{char_name_print}面板数据已保存到本地！")
    return

async def check_phantom_data(data) -> bool:
    try:
        role_detail = RoleDetailData.model_validate(data)
        # 检查数值
        calc: WuWaCalc = WuWaCalc(role_detail)
        calc.phantom_pre = calc.prepare_phantom()
        # 检查词条名
        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            equipPhantomList = role_detail.phantomData.equipPhantomList
            for _phantom in equipPhantomList:
                if _phantom and _phantom.phantomProp:
                    props = _phantom.get_props()
                    for _prop in props:
                        test = await exist_attribute_prop(_prop.attributeName)
                        if not test:
                            logger.info(f"[鸣潮][dc卡片识别]词条文本检查异常: {_prop.attributeName}")
                            return False
        return True
    except Exception as e:
        logger.error(f" [鸣潮][dc卡片识别] 角色声骸数据异常：{e}")
        return False

async def exist_attribute_prop(name: str = "") -> bool:
    TEXT_PATH = Path(__file__).parent.parent / "utils" / "texture2d" / "attribute_prop" 
    file_path = Path(TEXT_PATH) / f"attr_prop_{name}.png"
    try:
        return await asyncio.to_thread(file_path.exists)
    except Exception as e:
        logger.error(f"[鸣潮][dc卡片识别]文件检查异常: {name}: {e}")
        return False

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
