from gsuid_core.models import Event
from ..utils import hint
from ..utils.api.model import KuroRoleInfo
from ..utils.database.models import WavesUser, WavesBind
from ..utils.error_reply import WAVES_CODE_101, WAVES_CODE_102, WAVES_CODE_202
from ..utils.waves_api import waves_api, tap_api


async def add_cookie(ev: Event, ck: str):
    succ, game_info = await waves_api.get_game_role_info(ck)
    if not succ:
        return hint.error_reply(code=WAVES_CODE_101)
    data = KuroRoleInfo(**game_info)
    await WavesUser.insert_data(ev.user_id, ev.bot_id, cookie=ck, uid=data.roleId)
    await WavesBind.insert_data(ev.user_id, ev.bot_id, uid=data.roleId)
    return '添加成功！'


async def add_tap(ev: Event, tap_uid: str):
    waves_role_id = await tap_api.get_waves_id_by_tap(tap_uid)
    if waves_role_id <= 0:
        return hint.error_reply(code=waves_role_id)

    user_list = await WavesUser.select_data_list(user_id=ev.user_id, bot_id=ev.bot_id)
    if not user_list:
        return hint.error_reply(code=WAVES_CODE_102)
    
    str_role_id = str(waves_role_id)
    for user in user_list:
        if user.uid == str_role_id:
            await WavesUser.update_data(ev.user_id, ev.bot_id, uid=str_role_id, tap_uid=tap_uid)
            return 'TapTap绑定成功！'

    return hint.error_reply(code=WAVES_CODE_202)
