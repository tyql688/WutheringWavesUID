import asyncio
import json
from typing import Dict, Union, List

from gsuid_core.logger import logger
from ...utils.wwredis.wwredis import wavesRedis

redis_key = "ww:hash:playerCache"


async def save_all_card(raw_data: Dict, max_concurrent_batches=10):
    new_data = {
        roleId: json.dumps(i, ensure_ascii=False)
        for roleId, i in raw_data.items()
    }
    # async with wavesRedis.get_client() as client:
    #     await client.hset(redis_key, mapping=new_data)
    # return len(new_data)

    total_items = len(new_data)

    # 计算每批次的大小
    batch_size = total_items // max_concurrent_batches
    remainder = total_items % max_concurrent_batches

    # 分割数据
    batches = []
    start = 0
    for i in range(max_concurrent_batches):
        end = start + batch_size + (1 if i < remainder else 0)
        batch = dict(list(new_data.items())[start:end])
        batches.append(batch)
        start = end

    # 创建一个信号量，限制最大并发批次数
    semaphore = asyncio.Semaphore(max_concurrent_batches)

    async def process_batch(batch):
        async with semaphore:
            async with wavesRedis.get_client() as client:
                await client.hset(redis_key, mapping=batch)

    # 创建所有批次处理任务
    tasks = [process_batch(batch) for batch in batches]

    # 执行所有任务
    await asyncio.gather(*tasks)
    return len(new_data)


async def save_user_card(roleId: str, data: Union[List, str]):
    if not data:
        return
    if isinstance(data, list):
        data = json.dumps(data, ensure_ascii=False)
    async with wavesRedis.get_client() as client:
        await client.hset(redis_key, roleId, data)


async def get_user_card(roleId: str):
    async with wavesRedis.get_client() as client:
        data = await client.hget(redis_key, roleId)
    if data:
        return json.loads(data)
    return None


async def get_all_card():
    async with wavesRedis.get_client() as client:
        player_all_card = await client.hgetall(redis_key)

    logger.info(f"[鸣潮] {len(player_all_card)} 个角色数据已从缓存中获取")
    return player_all_card
