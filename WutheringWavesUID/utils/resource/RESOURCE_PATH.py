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
AVATAR_PATH = RESOURCE_PATH / 'avatar'
WEAPON_PATH = RESOURCE_PATH / 'weapon'


def init_dir():
    for i in [
        MAIN_PATH,
        PLAYER_PATH,
        RESOURCE_PATH,
        AVATAR_PATH,
        WEAPON_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
