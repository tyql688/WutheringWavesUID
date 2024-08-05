import sys

from gsuid_core.data_store import get_res_path

MAIN_PATH = get_res_path() / 'WutheringWavesUID'
sys.path.append(str(MAIN_PATH))

# 配置文件
CONFIG_PATH = MAIN_PATH / 'config.json'

PLAYER_PATH = MAIN_PATH / 'players'


def init_dir():
    for i in [
        MAIN_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
