from typing import Optional, Literal, Dict

from httpx import AsyncClient

from gsuid_core.utils.api.types import AnyDict
from gsuid_core.utils.download_resource.download_file import download
from ..utils.resource.RESOURCE_PATH import AVATAR_PATH, ROLE_PILE_PATH, WEAPON_PATH, ROLE_DETAIL_SKILL_PATH, \
    ROLE_DETAIL_CHAINS_PATH

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


async def download_one_avatar_pic(role_detail_temp, resource_id, is_force: bool = False):
    role_name = role_detail_temp['Name']
    name = f'role_head_{resource_id}.png'
    path = AVATAR_PATH / name
    if not is_force and path.exists():
        return
    resource_path = role_detail_temp['icon'].split('.')[0].replace('/Game/Aki/', '')
    url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'

    await download(url, AVATAR_PATH, name, tag=f"[鸣潮->【{role_name}-{resource_id}】->头像]]")


async def download_one_pile_pic(role_detail_temp, resource_id, is_force: bool = False):
    role_name = role_detail_temp['Name']
    name = f'role_pile_{resource_id}.png'
    path = ROLE_PILE_PATH / name
    if not is_force and path.exists():
        return
    resource_path = role_detail_temp['Background'].split('.')[0].replace('/Game/Aki/', '')
    url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'
    await download(url, ROLE_PILE_PATH, name, tag=f"[鸣潮->【{role_name}-{resource_id}】->立绘]")


async def download_one_skills(role_detail_temp, resource_id, is_force: bool = False):
    role_name = role_detail_temp['Name']
    skill_pic_dir = ROLE_DETAIL_SKILL_PATH / resource_id
    skill_pic_dir.mkdir(parents=True, exist_ok=True)
    skill_tree = role_detail_temp['SkillTrees']
    for skill_id, skill in skill_tree.items():
        name = f'skill_{skill["Skill"]["Name"]}.png'
        path = skill_pic_dir / name
        if not is_force and path.exists():
            continue
        resource_path = skill['Skill']['Icon'].split('.')[0].replace('/Game/Aki/', '')
        url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'

        await download(url, skill_pic_dir, name, tag=f"[鸣潮->【{role_name}-{resource_id}】->技能]")


async def download_one_chains(role_detail_temp, resource_id, is_force: bool = False):
    role_name = role_detail_temp['Name']
    chain_pic_dir = ROLE_DETAIL_CHAINS_PATH / resource_id
    chain_pic_dir.mkdir(parents=True, exist_ok=True)
    chains = role_detail_temp['Chains']
    for chain_id, chain in chains.items():
        name = f'chain_{chain_id}.png'
        path = chain_pic_dir / name
        if not is_force and path.exists():
            continue
        resource_path = chain['Icon'].split('.')[0].replace('/Game/Aki/', '')
        url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'

        await download(url, chain_pic_dir, name, tag=f"[鸣潮->【{role_name}-{resource_id}】->共鸣链]")


async def download_all_char_pic(all_character: Dict, is_force: bool = False):
    for resource_id, _ in all_character.items():
        role_detail_temp = await get_character_detail('character', resource_id)

        # avatar_pic
        await download_one_avatar_pic(role_detail_temp, resource_id, is_force)

        # pile_pic
        await download_one_pile_pic(role_detail_temp, resource_id, is_force)

        # skill_pic
        await download_one_skills(role_detail_temp, resource_id, is_force)

        # chain
        await download_one_chains(role_detail_temp, resource_id, is_force)


async def download_all_weapon_pic(all_weapon: Dict, is_force: bool = False):
    for resource_id, temp in all_weapon.items():
        weapon_name = temp['zh-Hans']
        name = f'weapon_{resource_id}.png'
        path = WEAPON_PATH / name
        if not is_force and path.exists():
            continue
        resource_path = temp['icon'].split('.')[0].replace('/Game/Aki/', '')
        url = f'{HAKUSH_MAIN_URL}/{resource_path}.webp'

        await download(url, WEAPON_PATH, name, tag=f"[鸣潮-【{weapon_name}-{resource_id}】->武器]")


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
