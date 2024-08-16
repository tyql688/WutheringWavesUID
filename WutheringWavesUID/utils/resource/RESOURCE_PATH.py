import sys

from gsuid_core.data_store import get_res_path

MAIN_PATH = get_res_path() / 'WutheringWavesUID'
sys.path.append(str(MAIN_PATH))

# 配置文件
CONFIG_PATH = MAIN_PATH / 'config.json'

# 用户数据保存文件
PLAYER_PATH = MAIN_PATH / 'players'

# 游戏素材
RESOURCE_PATH = MAIN_PATH / 'resource'
PHANTOM_PATH = RESOURCE_PATH / 'phantom'
AVATAR_PATH = RESOURCE_PATH / 'waves_avatar'
WEAPON_PATH = RESOURCE_PATH / 'waves_weapon'
ROLE_PILE_PATH = RESOURCE_PATH / 'role_pile'
ROLE_DETAIL_PATH = RESOURCE_PATH / 'role_detail'
ROLE_DETAIL_SKILL_PATH = ROLE_DETAIL_PATH / 'skill'
ROLE_DETAIL_CHAINS_PATH = ROLE_DETAIL_PATH / 'chains'


def init_dir():
    for i in [
        MAIN_PATH,
        PLAYER_PATH,
        RESOURCE_PATH,
        PHANTOM_PATH,
        AVATAR_PATH,
        WEAPON_PATH,
        ROLE_PILE_PATH,
        ROLE_DETAIL_PATH,
        ROLE_DETAIL_SKILL_PATH,
        ROLE_DETAIL_CHAINS_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
