from typing import Dict, Union, List

from ..utils.simple_async_cache_card import card_cache


async def save_all_card(all_card: Dict):
    await card_cache.set_all(all_card)
    return await card_cache.size()


async def save_user_card(roleId: str, data: Union[List]):
    if not data:
        return
    await card_cache.set(roleId, data)


async def get_user_card(roleId: str):
    return await card_cache.get(roleId)
