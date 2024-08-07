import time

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils.api.model import KuroRoleInfo, RoleList, AccountBaseInfo
from ..utils.database.models import WavesBind, WavesUser
from ..utils.hint import BIND_UID_HINT
from ..utils.waves_api import waves_api
from ..utils.waves_prefix import PREFIX

waves_role_info = SV('waves查询信息')


@waves_role_info.on_fullmatch(f'{PREFIX}查询', block=True)
async def send_role_info(bot: Bot, ev: Event):
    logger.info('[鸣潮]开始执行[查询信息]')
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    logger.info(f'[鸣潮][查询信息] user_id: {user_id} UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)

    ck = await WavesUser.get_user_cookie_by_uid(uid)
    if not ck:
        return await bot.send(BIND_UID_HINT)

    succ, game_info = await waves_api.get_game_role_info(ck)
    if not succ:
        return await bot.send(game_info)

    game_info = KuroRoleInfo(**game_info)

    # 共鸣者信息
    succ, role_info = await waves_api.get_role_info(uid, ck, game_info.serverId)
    if not succ:
        return await bot.send(role_info)

    # 账户数据
    succ, account_info = await waves_api.get_base_info(uid, ck, game_info.serverId)
    if not succ:
        return await bot.send(account_info)

    role_info = RoleList(**role_info)
    # 文字数据
    res_role_list = []
    for _, e in enumerate(role_info.roleList):
        res_role_list.append(f'''角色名: {e.roleName} 星级: {e.starLevel} 等级: {e.level} 属性: {e.attributeName}''')
    res_role = "\n".join(res_role_list)

    account_info = AccountBaseInfo(**account_info)

    res_box_list = []
    for _, b in enumerate(account_info.boxList):
        res_box_list.append(f'''{b.boxName}: {b.num}''')
    res_box = "\n".join(res_box_list)

    res = f'''游戏信息:
角色名: {account_info.name}
特征码: {account_info.id}
创建时间: {time.strftime('%Y-%m-%d', time.localtime(account_info.creatTime / 1000))}
活跃天数: {account_info.activeDays}
账号等级: {account_info.level}
世界等级: {account_info.worldLevel}
角色数量: {account_info.roleNum}
背包声匣数: {account_info.soundBox}
小型信标解锁数: {account_info.smallCount}
大型信标解锁数: {account_info.bigCount}
成就数量: {account_info.achievementCount}
宝箱数量:
{res_box}
共鸣者：
{res_role}
'''
    await bot.send(res)
