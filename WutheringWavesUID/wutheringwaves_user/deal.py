from typing import Union, List

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from ..utils import hint
from ..utils.api.model import KuroRoleInfo
from ..utils.database.models import WavesUser, WavesBind
from ..utils.error_reply import WAVES_CODE_101, ERROR_CODE, WAVES_CODE_103
from ..utils.refresh_char_detail import refresh_char
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import PREFIX


async def add_cookie(ev: Event, ck: str):
    succ, game_info = await waves_api.get_game_role_info(ck)
    if not succ:
        return hint.error_reply(code=WAVES_CODE_101)
    data = KuroRoleInfo(**game_info)

    platform_list = ['h5', 'ios']
    for platform in platform_list:
        succ, _ = await waves_api.refresh_data_for_platform(data.roleId, ck, data.serverId, platform)
        if succ:
            break
    else:
        return hint.error_reply(code=WAVES_CODE_101)

    user = await WavesUser.get_user_by_attr(ev.user_id, ev.bot_id, 'uid', data.roleId)
    if user:
        await WavesUser.update_data_by_data(
            select_data={
                'user_id': ev.user_id,
                'bot_id': ev.bot_id,
                'uid': data.roleId
            },
            update_data={
                'cookie': ck,
                'status': '',
                'platform': platform
            })
    else:
        await WavesUser.insert_data(ev.user_id, ev.bot_id, cookie=ck, uid=data.roleId)

    res = await WavesBind.insert_waves_uid(ev.user_id, ev.bot_id, data.roleId, ev.group_id, lenth_limit=9)
    if res == 0 or res == -2:
        await WavesBind.switch_uid_by_game(ev.user_id, ev.bot_id, data.roleId)

    await refresh_char(data.roleId, ev.user_id, ck)

    return f'[鸣潮] 特征码[{data.roleId}]绑定Token成功!\n使用【{PREFIX}查看】查看已绑定的特征码\n使用【{PREFIX}开启自动签到】开启游戏内每天的自动签到功能\n使用【{PREFIX}刷新面板】更新角色面板\n更新角色面板后可以使用【{PREFIX}暗主排行】查询暗主排行\n'


async def delete_cookie(ev: Event, uid: str) -> str:
    user = await WavesUser.get_user_by_attr(ev.user_id, ev.bot_id, 'uid', uid)
    if not user or not user.cookie:
        return f'[鸣潮] 特征码[{uid}]的token删除失败!\n❌不存在该特征码的token!\n'

    await WavesUser.update_data_by_data(
        select_data={
            'user_id': ev.user_id,
            'bot_id': ev.bot_id,
            'uid': uid
        },
        update_data={
            'cookie': ''
        })
    return f'[鸣潮] 特征码[{uid}]的token删除成功!\n'


async def get_cookie(bot: Bot, ev: Event) -> Union[List[str], str]:
    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    msg = []
    for uid in uid_list:
        ck = await waves_api.get_self_waves_ck(uid, ev.user_id)
        if not ck:
            continue
        msg.append(f'鸣潮uid: {uid}')
        msg.append(ck)

    if not msg:
        return '您当前未绑定token或者token已全部失效\n'

    return msg
