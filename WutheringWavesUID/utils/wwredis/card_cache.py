import json
from typing import Dict, Union, List

from ...utils.wwredis.wwredis import wavesRedis

redis_key = "ww:hash:playerCache"


async def save_all_card(data: Dict):
    new_data = {
        roleId: json.dumps(data, ensure_ascii=False)
        for roleId, data in data.items()
    }
    async with wavesRedis.get_client() as client:
        await client.hset(redis_key, mapping=new_data)
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
