from gsuid_core.models import Event
from ..utils import hint
from ..utils.api.model import KuroRoleInfo
from ..utils.database.models import WavesUser
from ..utils.error_reply import WAVES_CODE_101
from ..utils.waves_api import waves_api


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
                'cookie': ck,
                'status': ''
            })
    else:
        await WavesUser.insert_data(ev.user_id, ev.bot_id, cookie=ck, uid=data.roleId)

    return 'CK添加成功！'


async def delete_cookie(uid: str) -> str:
    if await WavesUser.delete_row(uid=uid):
        return '删除成功!'
    else:
        return '删除失败...不存在该UID的CK...'
