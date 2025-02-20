import json
from typing import Any, Dict, Union, Generator

import aiofiles
from itertools import zip_longest

from gsuid_core.logger import logger

from ..wutheringwaves_charinfo.draw_char_card import generate_online_role_detail
from ..utils.name_convert import alias_to_char_name, char_name_to_char_id
from ..utils.api.model import RoleDetailData
from .char_fetterDetail import get_fetterDetail_from_sonata
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH


async def save_card_dict_to_json(result_dict):
    
    char = result_dict["角色信息"]["角色名"]
    char_name = alias_to_char_name(char)
    char_id = char_name_to_char_id(char_name)

    # char_id = "1506" # 菲比..utils\map\detail_json\char\1506.json
    result = await generate_online_role_detail(char_id)
    
    data = {}

    # 处理 `chainList` 的数据
    data["chainList"] = []
    for chain in result.chainList:
        data["chainList"].append({
            "name": chain.name,
            "order": chain.order,
            "description": chain.description,
            "iconUrl": chain.iconUrl,
            "unlocked": chain.unlocked
        })
        
    # 处理 `level` 的数据
    data["level"] : result_dict["角色信息"]["等级"]
        
    # 处理 `phantomData` 的数据
    if result.phantomData is not None:
        phantom_data = result.phantomData
        data["phantomData"] = {
            "cost": 12,
            "equipPhantomList": []
        }
        ECHO = await get_fetterDetail_from_sonata(char_name)
        for echo_value in result_dict["装备数据"]:
            # 创建 ECHO 的独立副本
            echo = copy.deepcopy(ECHO)

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
            "breach": role.breach,
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

    # 将字典转换为 JSON 字符串
    print(json.dumps(data, indent=2, ensure_ascii=False))



async def get_all_role_detail_info_list(
    uid: str,
) -> Union[Generator[RoleDetailData, Any, None], None]:
    path = PLAYER_PATH / uid / "rawData.json"
    if not path.exists():
        return None
    try:
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            player_data = json.loads(await f.read())
    except Exception as e:
        logger.exception(f"get role detail info failed {path}:", e)
        path.unlink(missing_ok=True)
        return None

    return iter(RoleDetailData(**r) for r in player_data)


async def get_all_role_detail_info(uid: str) -> Union[Dict[str, RoleDetailData], None]:
    _all = await get_all_role_detail_info_list(uid)
    if not _all:
        return None
    return {r.role.roleName: r for r in _all}
