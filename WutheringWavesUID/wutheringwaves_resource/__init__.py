import asyncio
import json
from pathlib import Path

import aiofiles

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils import hakush_api
from ..utils.database.models import WavesBind
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.resource.download_all_resource import download_all_resource
from ..utils.simple_async_cache_card import AsyncCache, card_cache, user_bind_cache
from ..wutheringwaves_config import PREFIX

sv_download_config = SV('资源下载', pm=1)


@sv_download_config.on_fullmatch((f'{PREFIX}下载全部资源', f'{PREFIX}补充资源', f'{PREFIX}刷新补充资源'))
async def send_download_resource_msg(bot: Bot, ev: Event):
    await bot.send('[鸣潮] 正在开始下载~可能需要较久的时间!')
    await download_all_resource()

    if '补充' in ev.command:
        isForce = True if '刷新' in ev.command else False
        all_char = await hakush_api.get_all_character()
        await hakush_api.download_all_char_pic(all_char, isForce)

        all_weapon = await hakush_api.get_all_weapon()
        await hakush_api.download_all_weapon_pic(all_weapon, isForce)
    await bot.send('[鸣潮] 下载完成！')


async def startup():
    logger.info(
        '[鸣潮][资源文件下载] 正在检查与下载缺失的资源文件，可能需要较长时间，请稍等'
    )
    try:
        logger.info(f'[鸣潮][资源文件下载] {await download_all_resource()}')
    except Exception as e:
        logger.exception(e)
    try:
        logger.info(f'[鸣潮][加载用户面板缓存] 数量: {await load_all_card()}')
    except Exception as e:
        logger.exception(e)
    # logger.info(f'[鸣潮][加载用户绑定缓存] 数量: {await load_user_bind()}')


async def load_player_data(file_path: Path, cache: AsyncCache):
    """
    加载单个 rawData.json 文件并存入缓存。

    :param file_path: 文件路径。
    :param cache: 异步缓存对象。
    """
    try:
        uid = file_path.parent.name  # UID 是父目录的名称
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            raw_data = await f.read()
        data = json.loads(raw_data)
        await cache.set(uid, data)
    except Exception as e:
        logger.exception(f"Failed to load {file_path}: {e}")


async def load_all_players(player_path: Path, cache: AsyncCache):
    """
    加载指定目录下所有 rawData.json 文件到缓存。

    :param player_path: 玩家数据根目录。
    :param cache: 异步缓存对象。
    """
    # 找到所有 rawData.json 文件
    file_paths = list(player_path.glob("*/rawData.json"))

    # 使用 asyncio.gather 并行加载文件
    tasks = [load_player_data(file_path, cache) for file_path in file_paths]
    await asyncio.gather(*tasks)


async def load_all_card():
    # 并行加载所有玩家数据
    await load_all_players(PLAYER_PATH, card_cache)
    return await card_cache.size()


async def load_user_bind():
    users = await WavesBind.get_all_data()
    await user_bind_cache.set_all({user.user_id: user for user in users})
    return await user_bind_cache.size()
