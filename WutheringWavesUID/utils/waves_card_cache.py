import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Union

import aiofiles

from gsuid_core.logger import logger

from ..wutheringwaves_config import WutheringWavesConfig
from .api.model import RoleDetailData
from .char_info_utils import get_all_role_detail_info_list
from .resource.RESOURCE_PATH import PLAYER_PATH
from .waves_card_local_cache import (
    get_user_card,
    save_all_card,
    save_user_card,
)

CardUseOptions = WutheringWavesConfig.get_config("CardUseOptions").data
StartServerRedisLoad = WutheringWavesConfig.get_config("StartServerRedisLoad").data


async def load_player_data(file_path: Path, all_card: Dict):
    """
    加载单个 rawData.json 文件并存入缓存。

    :param file_path: 文件路径。
    :param all_card: 对象。
    """
    try:
        uid = file_path.parent.name  # UID 是父目录的名称
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
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

    # # 使用 asyncio.gather 并行加载文件
    # tasks = [load_player_data(file_path, all_card) for file_path in file_paths]
    # await asyncio.gather(*tasks)

    semaphore = asyncio.Semaphore(200)

    async def wrapped_load_player_data(file_path):
        async with semaphore:
            return await load_player_data(file_path, all_card)

    # 创建任务列表
    tasks = [wrapped_load_player_data(file_path) for file_path in file_paths]
    # 并发执行任务
    await asyncio.gather(*tasks)


async def load_all_card() -> int:
    logger.info(f"[鸣潮][排行面板数据启用规则 {CardUseOptions}]")
    if CardUseOptions == "不使用缓存":
        return -1
    all_card = {}
    # 并行加载所有玩家数据
    await load_all_players(PLAYER_PATH, all_card)
    if CardUseOptions == "内存缓存":
        return await save_all_card(all_card)
    elif CardUseOptions == "redis缓存":
        from .wwredis import card_cache

        await card_cache.delete_all_card()

        if StartServerRedisLoad:
            from .wwredis import rank_cache

            # total = await card_cache.save_all_card(all_card)
            a = time.time()
            logger.info("[鸣潮][开始处理排行......]")
            total = await rank_cache.save_rank_caches(all_card)
            logger.info(
                f"[鸣潮][结束处理排行......] 耗时:{time.time() - a:.2f}s 共加载{total}个用户"
            )
            return total


async def save_card(uid: str, data: Union[List], user_id: str):
    if CardUseOptions == "不使用缓存":
        return
    elif CardUseOptions == "内存缓存":
        await save_user_card(uid, data)
    elif CardUseOptions == "redis缓存":
        from .wwredis import rank_cache

        # await card_cache.save_user_card(uid, data)
        await rank_cache.save_rank_cache(uid, data, user_id)


async def get_card(uid: str):
    if CardUseOptions == "不使用缓存":
        return await get_all_role_detail_info_list(uid)
    elif CardUseOptions == "内存缓存":
        player_data = await get_user_card(uid)
        if not player_data:
            return None
        return iter(RoleDetailData(**r) for r in player_data)
    elif CardUseOptions == "redis缓存":
        # from .wwredis import card_cache
        #
        # player_data = await card_cache.get_user_card(uid)
        # if not player_data:
        #     return None
        # return iter(RoleDetailData(**r) for r in player_data)
        return await get_all_role_detail_info_list(uid)


async def get_user_all_card():
    if CardUseOptions == "redis缓存":
        # if StartServerRedisLoad:
        #     return await card_cache.get_all_card()
        # else:
        all_card = {}
        await load_all_players(PLAYER_PATH, all_card)
        return all_card
    return {}


async def refresh_ranks(all_card):
    if CardUseOptions == "redis缓存":
        from .wwredis import rank_cache

        # if not StartServerRedisLoad:
        #     await card_cache.save_all_card(all_card)

        return await rank_cache.save_rank_caches(all_card)


async def get_rank(char_id: str, rank_type: str, num=30):
    if CardUseOptions == "redis缓存":
        from .wwredis import rank_cache

        return await rank_cache.get_rank_cache(char_id, rank_type, num)


async def get_self_rank(char_id: str, rank_type: str, uid: str):
    if CardUseOptions == "redis缓存":
        from .wwredis import rank_cache

        return await rank_cache.get_self_rank(char_id, rank_type, uid)
