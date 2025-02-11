from gsuid_core.utils.download_resource.download_core import download_all_file
from .RESOURCE_PATH import (
    AVATAR_PATH,
    WEAPON_PATH,
    ROLE_PILE_PATH,
    XMU_GUIDE_PATH,
    MOEALKYNE_GUIDE_PATH,
    JINLINGZI_GUIDE_PATH,
    JIEXING_GUIDE_PATH,
    ROLE_DETAIL_SKILL_PATH,
    ROLE_DETAIL_CHAINS_PATH,
    PHANTOM_PATH,
    MATERIAL_PATH,
)


async def download_all_resource():
    await download_all_file(
        "WutheringWavesUID",
        {
            "resource/avatar": AVATAR_PATH,
            "resource/weapon": WEAPON_PATH,
            "resource/role_pile": ROLE_PILE_PATH,
            "resource/role_detail/skill": ROLE_DETAIL_SKILL_PATH,
            "resource/role_detail/chains": ROLE_DETAIL_CHAINS_PATH,
            "resource/phantom": PHANTOM_PATH,
            "resource/material": MATERIAL_PATH,
            "resource/guide/XMu": XMU_GUIDE_PATH,
            "resource/guide/Moealkyne": MOEALKYNE_GUIDE_PATH,
            "resource/guide/JinLingZi": JINLINGZI_GUIDE_PATH,
            "resource/guide/JieXing": JIEXING_GUIDE_PATH,
        },
    )
