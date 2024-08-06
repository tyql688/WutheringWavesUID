from gsuid_core.models import Event
from ..utils import hint
from ..utils.api.model import KuroRoleInfo
from ..utils.database.models import WavesUser, WavesBind
from ..utils.error_reply import WAVES_CODE_101, WAVES_CODE_103
from ..utils.waves_api import waves_api, tap_api


async def add_cookie(ev: Event, ck: str):
    succ, game_info = await waves_api.get_game_role_info(ck)
    if not succ:
        return hint.error_reply(code=WAVES_CODE_101)
    data = KuroRoleInfo(**game_info)

    user = await WavesUser.get_user_by_attr(ev.user_id, ev.bot_id, 'uid', data.roleId)
    if user:
        await WavesUser.update_data_by_data(
            select_data={
                'user_id': ev.user_id,
                'bot_id': ev.bot_id,
                'uid': data.roleId
            },
            update_data={
                'cookie': ck
            })
    else:
        # 没绑定过tap？
        await WavesUser.insert_data(ev.user_id, ev.bot_id, cookie=ck, uid=data.roleId)

    return 'CK添加成功！'


async def delete_cookie(uid: str) -> str:
    if await WavesUser.delete_row(uid=uid):
        return '删除成功!'
    else:
        return '删除失败...不存在该UID的CK...'


async def add_tap(ev: Event, tap_uid: str):
    waves_id = await tap_api.get_waves_id_by_tap(tap_uid)
    if waves_id <= 0:
        return hint.error_reply(code=waves_id)
    waves_id = str(waves_id)

    uid_list = await WavesBind.get_uid_list_by_game(user_id=ev.user_id, bot_id=ev.bot_id)
    if waves_id not in uid_list:
        return hint.error_reply(code=WAVES_CODE_103)

    user = await WavesUser.get_user_by_attr(ev.user_id, ev.bot_id, 'uid', waves_id)
    if user:
        await WavesUser.update_data_by_data(
            select_data={
                'user_id': ev.user_id,
                'bot_id': ev.bot_id,
                'uid': waves_id
            },
            update_data={
                'tap_uid': tap_uid
            })
        return 'TapTap绑定成功！'
    else:
        await WavesUser.insert_data(ev.user_id, ev.bot_id, uid=waves_id, tap_uid=tap_uid)

    return 'TapTap绑定成功！'
