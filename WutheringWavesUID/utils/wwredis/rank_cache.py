import asyncio
import json
from typing import Dict, List, Optional

from ...utils.wwredis.wwredis import wavesRedis
from ...wutheringwaves_config import WutheringWavesConfig
from ..expression_ctx import get_waves_char_rank
from ..name_convert import get_all_char_id
from ..resource.constant import SPECIAL_CHAR, SPECIAL_CHAR_INT

redis_key_score = "ww:zset:score_rank:{}"  # 角色id - 分数排行
redis_key_expected = "ww:zset:expected_rank:{}"  # 角色id - 期望排行


async def get_waves_token_map():
    wavesTokenUsersMap = {}

    # 全局 主人定义的
    RankUseToken = WutheringWavesConfig.get_config("RankUseToken").data
    if RankUseToken:
        from ..database.models import WavesUser

        wavesTokenUsers = await WavesUser.get_waves_all_user()
        wavesTokenUsersMap.update({w.uid: w.cookie for w in wavesTokenUsers})

    return wavesTokenUsersMap


async def check_in_rank(
    uid: str,
    user_id: str,
    is_self_ck: bool,
    token: Optional[str] = "",
):
    RankUseToken = WutheringWavesConfig.get_config("RankUseToken").data
    if RankUseToken:
        if token and is_self_ck:
            return True
        else:
            return False
    return True


async def clear_rank_cache():
    char_ids = get_all_char_id()
    async with wavesRedis.get_client() as client:
        pipe = await client.pipeline()
        for char_id in char_ids:
            await pipe.delete(redis_key_score.format(char_id))
            await pipe.delete(redis_key_expected.format(char_id))
        await pipe.execute()


async def save_rank_cache(
    uid: str,
    waves_char_rank: List,
    user_id: str,
    is_self_ck: bool = False,
    token: Optional[str] = "",
):
    if not await check_in_rank(uid, user_id, is_self_ck, token):
        return

    async with wavesRedis.get_client() as client:
        pipe = await client.pipeline()
        for rank in waves_char_rank:
            char_id = rank.roleId
            if char_id in SPECIAL_CHAR_INT:
                char_id = SPECIAL_CHAR_INT[char_id][0]
            if rank.score > 0:
                await pipe.zadd(redis_key_score.format(char_id), {uid: rank.score})
            if rank.expected_damage and rank.expected_damage > 0:
                await pipe.zadd(
                    redis_key_expected.format(char_id), {uid: rank.expected_damage}
                )
        await pipe.execute()


async def save_rank_caches(all_card):
    # 清理排行
    await clear_rank_cache()
    # 获取token
    wavesTokenUsersMap = await get_waves_token_map()

    async def func_save(score_temp: Dict, expected_temp: Dict):
        async with wavesRedis.get_client() as client:
            pipe = await client.pipeline()
            for char_id in score_temp:
                await pipe.zadd(redis_key_score.format(char_id), score_temp[char_id])
            for char_id in expected_temp:
                await pipe.zadd(
                    redis_key_expected.format(char_id), expected_temp[char_id]
                )
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
        except Exception:
            continue
        waves_char_rank = await get_waves_char_rank(user_id, player_data, True)
        for rank in waves_char_rank:
            char_id = rank.roleId
            if char_id in SPECIAL_CHAR_INT:
                char_id = SPECIAL_CHAR_INT[char_id][0]
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
        await asyncio.sleep(0.5)

    await func_save(score, expected)
    return total


async def get_rank_cache(char_id: str, rank_type: str, num=50):
    if char_id in SPECIAL_CHAR:
        char_id = SPECIAL_CHAR[char_id][0]
    async with wavesRedis.get_client() as client:
        if rank_type == "评分":
            rank_list = await client.zrevrange(
                redis_key_score.format(char_id), 0, num - 1
            )
        else:
            rank_list = await client.zrevrange(
                redis_key_expected.format(char_id), 0, num - 1
            )
    return rank_list


async def get_self_rank(char_id: str, rank_type: str, uid: str):
    if char_id in SPECIAL_CHAR:
        char_id = SPECIAL_CHAR[char_id][0]
    async with wavesRedis.get_client() as client:
        if rank_type == "评分":
            rank = await client.zrevrank(redis_key_score.format(char_id), uid)
        else:
            rank = await client.zrevrank(redis_key_expected.format(char_id), uid)
    return rank
