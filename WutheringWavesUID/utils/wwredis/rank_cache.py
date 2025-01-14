import json
from typing import List, Dict

from ..expression_ctx import get_waves_char_rank
from ..name_convert import get_all_char_id
from ...utils.wwredis.wwredis import wavesRedis

redis_key_score = 'ww:zset:score_rank:{}'  # 角色id - 分数排行
redis_key_expected = 'ww:zset:expected_rank:{}'  # 角色id - 期望排行


async def clear_rank_cache():
    char_ids = get_all_char_id()
    async with wavesRedis.get_client() as client:
        pipe = await client.pipeline()
        for char_id in char_ids:
            await pipe.delete(redis_key_score.format(char_id))
            await pipe.delete(redis_key_expected.format(char_id))
        await pipe.execute()


async def save_rank_cache(user_id: str, player_data: List):
    waves_char_rank = await get_waves_char_rank(user_id, player_data, True)
    async with wavesRedis.get_client() as client:
        pipe = await client.pipeline()
        for rank in waves_char_rank:
            char_id = rank.roleId
            if rank.score > 0:
                await pipe.zadd(redis_key_score.format(char_id), {user_id: rank.score})
            if rank.expected_damage and rank.expected_damage > 0:
                await pipe.zadd(redis_key_expected.format(char_id), {user_id: rank.expected_damage})
        await pipe.execute()


async def save_rank_caches(all_card):
    await clear_rank_cache()

    wavesTokenUsersMap = {}
    from ...wutheringwaves_config import WutheringWavesConfig
    # 全局 主人定义的
    RankUseToken = WutheringWavesConfig.get_config('RankUseToken').data
    if RankUseToken:
        from ..database.models import WavesUser
        wavesTokenUsers = await WavesUser.get_waves_all_user()
        wavesTokenUsersMap = {w.uid: w.cookie for w in wavesTokenUsers}

    async def func_save(score_temp: Dict, expected_temp: Dict):
        async with wavesRedis.get_client() as client:
            pipe = await client.pipeline()
            for char_id in score_temp:
                await pipe.zadd(redis_key_score.format(char_id), score_temp[char_id])
            for char_id in expected_temp:
                await pipe.zadd(redis_key_expected.format(char_id), expected_temp[char_id])
            await pipe.execute()

    score = {}
    expected = {}

    total = 0
    flag_count = 0
    for user_id, player_data in all_card.items():
        if wavesTokenUsersMap and user_id not in wavesTokenUsersMap:
            continue
        try:
            if isinstance(player_data, str):
                player_data = json.loads(player_data)
        except Exception as e:
            continue
        waves_char_rank = await get_waves_char_rank(user_id, player_data, True)
        for rank in waves_char_rank:
            char_id = rank.roleId
            if rank.score > 0:
                score[char_id] = score.get(char_id, {})
                score[char_id][user_id] = rank.score
            if rank.expected_damage and rank.expected_damage > 0:
                expected[char_id] = expected.get(char_id, {})
                expected[char_id][user_id] = rank.expected_damage

        flag_count += 1
        if flag_count == 100:
            await func_save(score, expected)
            score = {}
            expected = {}
            flag_count = 0
        total += 1

    await func_save(score, expected)
    return total


async def get_rank_cache(char_id: str, rank_type: str, num=50):
    async with wavesRedis.get_client() as client:
        if rank_type == '评分':
            rank_list = await client.zrevrange(redis_key_score.format(char_id), 0, num - 1)
        else:
            rank_list = await client.zrevrange(redis_key_expected.format(char_id), 0, num - 1)
    return rank_list


async def get_self_rank(char_id: str, rank_type: str, user_id: str):
    async with wavesRedis.get_client() as client:
        if rank_type == '评分':
            rank = await client.zrevrank(redis_key_score.format(char_id), user_id)
        else:
            rank = await client.zrevrank(redis_key_expected.format(char_id), user_id)
    return rank
