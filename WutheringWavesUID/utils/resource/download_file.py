from typing import Union

from PIL import Image

from gsuid_core.utils.download_resource.download_file import download
from .RESOURCE_PATH import AVATAR_PATH, WEAPON_PATH
from .. import image as waves_image
from ..api.api import WIKI_CATALOGUE_MAP
from ..api.model import RoleList
from ..waves_api import waves_api


async def get_square_avatar(charName: str, roleId: str, token: str,
                            serverId: str) -> Union[Image.Image, str, None]:
    img = await waves_image.get_square_avatar(charName)
    if img:
        return img

    succ, role_info = await waves_api.get_role_info(roleId, token, serverId)
    if not succ:
        raise ValueError("角色信息获取失败")

    role_info = RoleList(**role_info)
    for r in role_info.roleList:
        pic = f"role_head_{r.roleName}.png"
        path = AVATAR_PATH / pic
        if path.exists():
            continue
        await download(r.roleIconUrl, AVATAR_PATH, pic, tag="[鸣潮]")

    img = await waves_image.get_square_avatar(charName)
    if not img:
        raise ValueError("角色信息获取失败")
    return img


async def get_square_weapon(weaponName: str) -> Union[Image.Image, str, None]:
    img = await waves_image.get_square_weapon(weaponName)
    if img:
        return img

    succ, weapon_info = await waves_api.get_wiki(WIKI_CATALOGUE_MAP["武器"])
    if not succ:
        raise ValueError("武器信息获取失败")

    for w in weapon_info['results']['records']:
        name = w['name']
        url = w['content']['contentUrl']
        pic = f"weapon_{name}.png"
        path = WEAPON_PATH / pic
        if path.exists():
            continue
        await download(url, WEAPON_PATH, pic, tag="[鸣潮]")

    img = await waves_image.get_square_weapon(weaponName)
    if not img:
        raise ValueError("武器信息获取失败")
    return img
