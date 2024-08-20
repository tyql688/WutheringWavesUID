from typing import Optional, Literal, Dict

from httpx import AsyncClient

from gsuid_core.utils.api.types import AnyDict
from gsuid_core.utils.download_resource.download_file import download
from ..utils.resource.RESOURCE_PATH import AVATAR_PATH, ROLE_PILE_PATH, WEAPON_PATH

_HEADER = {
    'Content-Type': 'application/json',
}

HAKUSH_MAIN_URL = 'https://api.hakush.in/ww'


async def get_all_character():
    url = f'{HAKUSH_MAIN_URL}/data/character.json'
    return await _hakush_request(url)


async def get_character_detail(source_type: str, resource_id: str):
    url = f'{HAKUSH_MAIN_URL}/data/zh/{source_type}/{resource_id}.json'
    return await _hakush_request(url)


async def get_all_weapon():
    url = f'{HAKUSH_MAIN_URL}/data/weapon.json'
    return await _hakush_request(url)


async def download_all_avatar_pic(all_character: Dict, is_force: bool = False):
    for resource_id, temp in all_character.items():
        name = f'role_head_{resource_id}.png'
        path = AVATAR_PATH / name
        if not is_force and path.exists():
            continue
        resource_path = temp['icon'].split('.')[0].replace('/Game/Aki/', '')
        url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'

        await download(url, AVATAR_PATH, name, tag="[鸣潮]")


async def download_all_pile_pic(all_character: Dict, is_force: bool = False):
    for resource_id, _ in all_character.items():
        name = f'role_pile_{resource_id}.png'
        path = ROLE_PILE_PATH / name
        if not is_force and path.exists():
            continue
        temp = await get_character_detail('character', resource_id)
        resource_path = temp['Background'].split('.')[0].replace('/Game/Aki/', '')
        url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'

        await download(url, ROLE_PILE_PATH, name, tag="[鸣潮]")


async def download_all_weapon_pic(all_weapon: Dict, is_force: bool = False):
    for resource_id, temp in all_weapon.items():
        name = f'weapon_{resource_id}.png'
        path = WEAPON_PATH / name
        if not is_force and path.exists():
            continue
        resource_path = temp['icon'].split('.')[0].replace('/Game/Aki/', '')
        url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'

        await download(url, WEAPON_PATH, name, tag="[鸣潮]")


async def _hakush_request(
    url: str,
    method: Literal['GET', 'POST'] = 'GET',
    header: AnyDict = _HEADER,
    params: Optional[AnyDict] = None,
    data: Optional[AnyDict] = None,
) -> Optional[AnyDict]:
    async with AsyncClient(timeout=None) as client:
        req = await client.request(
            method,
            url=url,
            headers=header,
            params=params,
            json=data,
        )
        data = req.json()
        return data
