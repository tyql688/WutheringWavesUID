import json
from typing import Dict, Union, List

from ...utils.wwredis.wwredis import wavesRedis

redis_key = "ww:hash:playerCache"


def save_all_card(data: Dict):
    new_data = {
        roleId: json.dumps(data, ensure_ascii=False)
        for roleId, data in data.items()
    }
    wavesRedis.get_client.hmset(redis_key, new_data)
    return len(new_data)


def save_user_card(roleId: str, data: Union[List, str]):
    if not data:
        return
    if isinstance(data, list):
        data = json.dumps(data, ensure_ascii=False)
    wavesRedis.get_client.hset(redis_key, roleId, data)


def get_user_card(roleId: str):
    data = wavesRedis.get_client.hget(redis_key, roleId)
    if data:
        return json.loads(data)
    return None
