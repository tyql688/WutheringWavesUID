import asyncio
import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

import aiofiles
import msgspec

from gsuid_core.logger import logger
from gsuid_core.models import Event
from ..utils.api.model import GachaLog
from ..utils.database.models import WavesUser
from ..utils.error_reply import WAVES_CODE_104, WAVES_CODE_108
from ..utils.hint import error_reply
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.waves_api import waves_api
from ..version import WutheringWavesUID_version
from ..wutheringwaves_config import PREFIX

gacha_type_meta_data = {
    '角色精准调谐': ['1'],
    '武器精准调谐': ['2'],
    '角色调谐（常驻池）': ['3'],
    '武器调谐（常驻池）': ['4'],
    '新手调谐': ['5'],
    '新手自选唤取': ['6'],
    '新手自选唤取（感恩定向唤取）': ['7'],
}


def find_length(A, B) -> int:
    """数组最长公共子序列长度"""
    n, m = len(A), len(B)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    ans = 0
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            dp[i][j] = dp[i + 1][j + 1] + 1 if A[i] == B[j] else 0
            ans = max(ans, dp[i][j])
    return ans


async def get_new_gachalog(
    uid: str,
    record_id: str,
    full_data: Dict[str, List[GachaLog]],
    is_force: bool) -> (Union[int, None], Dict[str, List[GachaLog]], Dict[str, int]):
    new = {}
    new_count = {}
    for gacha_name in gacha_type_meta_data:
        for card_pool_type in gacha_type_meta_data[gacha_name]:
            res = await waves_api.get_gacha_log(card_pool_type, record_id, uid)
            if not isinstance(res, dict) or res.get('code') != 0 or res.get('data', None) is None:
                # 抽卡记录获取失败
                if res.get('code') == -1:
                    return WAVES_CODE_108, None, None
                else:
                    return WAVES_CODE_104, None, None
            gacha_log = [GachaLog(**log) for log in res['data']]
            old_length = find_length(full_data[gacha_name], gacha_log)
            _add = gacha_log if old_length == 0 else gacha_log[:-old_length]
            new[gacha_name] = _add + copy.deepcopy(full_data[gacha_name])
            new_count[gacha_name] = len(_add)
            await asyncio.sleep(1)
    return None, new, new_count


async def save_gachalogs(
    ev: Event,
    uid: str,
    record_id: str,
    is_force: bool = False
) -> str:
    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # 抽卡记录json路径
    gachalogs_path = path / 'gacha_logs.json'

    if gachalogs_path.exists():
        with Path.open(gachalogs_path, encoding='UTF-8') as f:
            gachalogs_history: Dict = json.load(f)
        gachalogs_history = gachalogs_history['data']
    else:
        gachalogs_history = {
            '角色精准调谐': [],
            '武器精准调谐': [],
            '角色调谐（常驻池）': [],
            '武器调谐（常驻池）': [],
            '新手调谐': [],
            '新手自选唤取': [],
            '新手自选唤取（感恩定向唤取）': [],
        }

    for gacha_name in gacha_type_meta_data.keys():
        gachalogs_history[gacha_name] = [GachaLog(**log) for log in gachalogs_history[gacha_name]]

    code, gachalogs_new, gachalogs_count_add = await get_new_gachalog(uid, record_id, gachalogs_history, is_force)
    if isinstance(code, int) or not gachalogs_new:
        return error_reply(code)

    await save_record_id(ev.user_id, ev.bot_id, uid, record_id)

    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    # 初始化最后保存的数据
    result = {'uid': uid, 'data_time': current_time}

    # 保存数量
    for gacha_name in gacha_type_meta_data.keys():
        result[gacha_name] = len(gachalogs_new[gacha_name])

    result['data'] = {
        gacha_name: [log.dict() for log in gachalogs_new[gacha_name]]
        for gacha_name in gacha_type_meta_data.keys()}

    vo = msgspec.to_builtins(result)
    async with aiofiles.open(gachalogs_path, 'w', encoding='UTF-8') as file:
        await file.write(json.dumps(vo, ensure_ascii=False))

    # 计算数据
    all_add = sum(gachalogs_count_add.values())

    # 回复文字
    im = []
    if all_add == 0:
        im.append(f'🌱UID{uid}没有新增调谐数据!')
    else:
        im.append(f'✅UID{uid}数据更新成功！')
        for k, v in gachalogs_count_add.items():
            im.append(f'[{k}]新增{v}个数据！')
    im.append(f'可以使用【{PREFIX}抽卡记录】获取全部抽卡数据')
    im = '\n'.join(im)
    return im


async def save_record_id(user_id, bot_id, uid, record_id):
    user = await WavesUser.get_user_by_attr(user_id, bot_id, 'uid', uid)
    if user:
        if user.record_id == record_id:
            return
        await WavesUser.update_data_by_data(
            select_data={
                'user_id': user_id,
                'bot_id': bot_id,
                'uid': uid
            },
            update_data={
                'record_id': record_id
            })
    else:
        await WavesUser.insert_data(user_id, bot_id, record_id=record_id, uid=uid)


async def export_gachalogs(uid: str) -> dict:
    path = PLAYER_PATH / uid
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H:%M:%S')

    # 抽卡记录json路径
    gachalogs_path = path / 'gacha_logs.json'
    if gachalogs_path.exists():
        async with aiofiles.open(gachalogs_path, 'r', encoding='UTF-8') as f:
            raw_data = json.loads(await f.read())

        result = {
            'info': {
                'export_time': current_time,
                'export_app': 'WutheringWavesUID',
                'export_app_version': WutheringWavesUID_version,
                'export_timestamp': round(now.timestamp()),
                'version': 'v1.0',
                'uid': uid,
            },
            'list': [],
        }
        gachalogs_history = raw_data['data']
        for name, gachalogs in gachalogs_history.items():
            result['list'].extend(gachalogs)

        async with aiofiles.open(path / f'export_{uid}.json', 'w', encoding='UTF-8') as file:
            await file.write(json.dumps(result, ensure_ascii=False, indent=4))

        logger.success('[导出抽卡记录] 导出成功!')
        im = {
            'retcode': 'ok',
            'data': '导出成功!',
            'name': f'export_{uid}.json',
            'url': str((path / f'export_{uid}.json').absolute()),
        }
    else:
        logger.error('[导出抽卡记录] 没有找到抽卡记录!')
        im = {
            'retcode': 'error',
            'data': '你还没有抽卡记录可以导出!',
            'name': '',
            'url': '',
        }

    return im
