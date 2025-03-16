from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..wutheringwaves_config import PREFIX
from ..utils.refresh_char_detail import save_card_info
from ..utils.database.models import WavesBind
from ..utils.waves_api import waves_api
from ..utils.name_convert import (
    alias_to_char_name, 
    char_name_to_char_id,
    alias_to_sonata_name,
    phantom_id_to_phantom_name
)

from .char_fetterDetail import get_fetterDetail_from_sonata, get_first_echo_id_list

import aiofiles
import json
import re

async def change_echo(bot: Bot, ev: Event):
    at_sender = True if ev.group_id else False
    user_id = ev.at if ev.at else ev.user_id

    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    # 更新groupid
    await WavesBind.insert_waves_uid(
        user_id, ev.bot_id, uid, ev.group_id, lenth_limit=9
    )

    if not waves_api.is_net(uid):
        return await bot.send(f"[鸣潮] 国服用户不支持修改角色数据", at_sender)

    char = ev.regex_dict.get("char")
    sonata = ev.regex_dict.get("sonata")
    phantom = bool(ev.regex_dict.get("echo"))  # 改为布尔值判断

    char_name = alias_to_char_name(char)
    char_id = int(char_name_to_char_id(char_name)) # Int类型配合获取到的本地数据集
    char_name_print = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9\s]', '', char_name) # 删除"漂泊者·衍射"的符号

    bool_get, old_data = await get_local_all_role_detail(uid)
    if not bool_get:
        return await bot.send(f"[鸣潮] 用户{uid}数据不存在，请先使用【{PREFIX}分析】上传{char_name_print}角色数据", at_sender)

    bool_change, waves_data = await change_sonata_and_first_echo(bot, char_id, sonata, phantom, old_data)
    if not bool_change:
        return await bot.send(f"[鸣潮] 修改角色{char_name_print}数据失败，请检查命令的正确性", at_sender)

    # 覆盖更新
    await save_card_info(uid, waves_data)
    return await bot.send(f"[鸣潮] 修改角色{char_name_print}数据成功，使用【{PREFIX}{char_name_print}面板】查看您的角色面板", at_sender)

async def get_local_all_role_detail(uid: str) -> tuple[bool, dict]:
    _dir = PLAYER_PATH / uid
    _dir.mkdir(parents=True, exist_ok=True)
    path = _dir / "rawData.json"

    role_data = {}
    if path.exists():
        try:
            async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
                data = json.loads(await f.read())
                role_data = {d["role"]["roleId"]: d for d in data}
        except Exception as e:
            logger.exception(f"[鸣潮] 基础数据get failed {path}:", e)
            path.unlink(missing_ok=True)
    else:
        return False, role_data

    return True, role_data

async def change_sonata_and_first_echo(bot: Bot, char_id: int, sonata_a: str, phantom_a: bool, role_data: dict) -> tuple[bool, dict]:
    # 检查角色是否存在
    if char_id not in role_data:
        return False, None
    char_data = role_data[char_id]

    # 初始化
    waves_data = []

    if sonata_a:
        sonata = alias_to_sonata_name(sonata_a)
        logger.info(f"[鸣潮] 修改套装为:{sonata}")
        if not sonata:
            return False, None

        ECHO = await get_fetterDetail_from_sonata(sonata)

        echo_num = len(char_data["phantomData"]["equipPhantomList"])
        for echo in char_data["phantomData"]["equipPhantomList"]:
            echo["fetterDetail"] = ECHO["fetterDetail"]
            echo["phantomProp"]["name"] = ECHO["phantomProp"]["name"]
            echo["fetterDetail"]["num"] = echo_num
        
    if phantom_a:
        sonata = None
        for echo in char_data["phantomData"]["equipPhantomList"]:
            if not sonata:
                sonata = echo["fetterDetail"]["name"]
        phantom_id_list = await get_first_echo_id_list(sonata)

        options = [
            f"{index+1}: {phantom_id_to_phantom_name(phantom)}"
            for index, phantom in enumerate(phantom_id_list)
        ]
        TEXT_GET_RESP = (
            "[鸣潮] 请选择替换为哪个4cost声骸：\n"
            + "\n".join(options)
            + "\n请输入序号（1-{}）选择".format(len(phantom_id_list))
        )

        resp = await bot.receive_resp(TEXT_GET_RESP)
        if resp is not None and resp.content[0].type == "text" and resp.content[0].data.isdigit():
            choice = int(resp.content[0].data) - 1
            if 0 <= choice < len(phantom_id_list):
                first_change_bool = True # 只修改第一顺位4cost声骸
                selected_phantom = phantom_id_list[choice]
                for echo in char_data["phantomData"]["equipPhantomList"]:
                    if int(echo["cost"]) == 4 and first_change_bool:
                        echo["phantomProp"]["phantomId"] = selected_phantom
                        first_change_bool = False
                        continue
                    if int(echo["cost"]) == 4 and not first_change_bool:
                        different_phantoms = [p for p in phantom_id_list if p != selected_phantom]
                        if not different_phantoms:
                            return False, None
                        if echo["phantomProp"]["phantomId"] == selected_phantom or echo["phantomProp"]["phantomId"] not in different_phantoms:
                            echo["phantomProp"]["phantomId"] = different_phantoms[0]  # 取第一个不同的元素


                logger.info(f"[鸣潮] 修改4cost声骸id为:{selected_phantom}")
            else:
                return False, None
        else:
            return False, None
    
    # 更新数据
    role_data[char_id] = char_data
    waves_data = list(role_data.values())
    
    return True, waves_data


async def get_local_all_role_info(uid: str) -> tuple[bool, dict]:
    _dir = PLAYER_PATH / uid
    _dir.mkdir(parents=True, exist_ok=True)
    path = _dir / "rawData.json"

    # 初始化标准数据结构
    role_data = {
        'roleList': [],
        'showRoleIdList': [],
        'showToGuest': False
    }
    
    if not path.exists():
        return False, role_data
        
    try:
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            raw_data = json.loads(await f.read())
            
            # 正确解析角色列表
            if isinstance(raw_data, list):
                for item in raw_data:
                    if "role" in item:
                        role_data["roleList"].append(item["role"])
            
        return True, role_data
    except Exception as e:
        logger.exception(f"[鸣潮] 数据解析失败 {path}:", e)
        path.unlink(missing_ok=True)
        return False, role_data
