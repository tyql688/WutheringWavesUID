from gsuid_core.models import Event
from ..utils import hint
from ..utils.database.models import WavesUser, WavesBind
from ..utils.waves_api import waves_api


async def add_cookie(ev: Event, ck: str):
    flag, data = await waves_api.get_game_info(ck)
    if not flag:
        return hint.error_reply(msg=data)
    # waves 角色id
    roleId = data['roleId']
    await WavesUser.insert_data(ev.user_id, ev.bot_id, cookie=ck, uid=roleId)
    await WavesBind.insert_data(ev.user_id, ev.bot_id, uid=roleId)
    return '添加成功！'
