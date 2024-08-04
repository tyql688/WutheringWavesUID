from gsuid_core.models import Event
from ..utils import hint
from ..utils.api.model import KuroRoleInfo
from ..utils.database.models import WavesUser, WavesBind
from ..utils.waves_api import waves_api


async def add_cookie(ev: Event, ck: str):
    succ, game_info = await waves_api.get_game_role_info(ck)
    if not succ:
        return hint.error_reply(code=-101)
    data = KuroRoleInfo(**game_info)
    await WavesUser.insert_data(ev.user_id, ev.bot_id, cookie=ck, uid=data.roleId)
    await WavesBind.insert_data(ev.user_id, ev.bot_id, uid=data.roleId)
    return '添加成功！'
