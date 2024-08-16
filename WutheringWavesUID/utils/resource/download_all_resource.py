from gsuid_core.utils.download_resource.download_core import download_all_file
from .RESOURCE_PATH import AVATAR_PATH, WEAPON_PATH, ROLE_PILE_PATH


async def download_all_resource():
    await download_all_file(
        'WutheringWavesUID',
        {
            'resource/avatar': AVATAR_PATH,
            'resource/weapon': WEAPON_PATH,
            'resource/role_pile': ROLE_PILE_PATH,
        },
    )
