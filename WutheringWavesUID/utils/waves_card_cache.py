import asyncio
import json
from pathlib import Path
from typing import Dict, Union, List

import aiofiles

from gsuid_core.logger import logger
from .api.model import RoleDetailData
from .char_info_utils import get_all_role_detail_info_list
from .resource.RESOURCE_PATH import PLAYER_PATH
from .waves_card_local_cache import save_all_card, save_user_card, get_user_card
from ..wutheringwaves_config import WutheringWavesConfig

CardUseOptions = WutheringWavesConfig.get_config('CardUseOptions').data


async def load_player_data(file_path: Path, all_card: Dict):
    """
    加载单个 rawData.json 文件并存入缓存。

    :param file_path: 文件路径。
    :param all_card: 对象。
    """
    try:
        uid = file_path.parent.name  # UID 是父目录的名称
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            raw_data = await f.read()
        data = json.loads(raw_data)
        all_card[uid] = data
    except Exception as e:
        logger.exception(f"Failed to load {file_path}: {e}")


async def load_all_players(player_path: Path, all_card: Dict):
    """
    加载指定目录下所有 rawData.json 文件到缓存。

    :param player_path: 玩家数据根目录。
    :param all_card: 对象。
    """
    # 找到所有 rawData.json 文件
    file_paths = list(player_path.glob("*/rawData.json"))

    # 使用 asyncio.gather 并行加载文件
    tasks = [load_player_data(file_path, all_card) for file_path in file_paths]
    await asyncio.gather(*tasks)


async def load_all_card() -> int:
    logger.info(f'[鸣潮][排行面板数据启用规则 {CardUseOptions}]')
    if CardUseOptions == "不使用缓存":
        return -1
    all_card = {}
    # 并行加载所有玩家数据
    await load_all_players(PLAYER_PATH, all_card)
    if CardUseOptions == "内存缓存":
        return await save_all_card(all_card)
    elif CardUseOptions == "redis缓存":
        from .wwredis import card_cache
        return card_cache.save_all_card(all_card)


async def save_card(uid: str, data: Union[List]):
    if CardUseOptions == "不使用缓存":
        return
    elif CardUseOptions == "内存缓存":
        await save_user_card(uid, data)
    elif CardUseOptions == "redis缓存":
        from .wwredis import card_cache
        card_cache.save_user_card(uid, data)


async def get_card(uid: str):
    if CardUseOptions == "不使用缓存":
        return await get_all_role_detail_info_list(uid)
    elif CardUseOptions == "内存缓存":
        player_data = await get_user_card(uid)
        if not player_data:
            return None
        return iter(RoleDetailData(**r) for r in player_data)
    elif CardUseOptions == "redis缓存":
        from .wwredis import card_cache
        player_data = card_cache.get_user_card(uid)
        if not player_data:
            return None
        return iter(RoleDetailData(**r) for r in player_data)
