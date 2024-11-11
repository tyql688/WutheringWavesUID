from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .draw_echo_list import get_draw_list
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from ..wutheringwaves_config import PREFIX

sv_waves_echo_list = SV(f'{PREFIX}声骸展示')


@sv_waves_echo_list.on_fullmatch(
    (
        f'{PREFIX}声骸列表',
        f'{PREFIX}我的声骸',
        f'{PREFIX}声骸仓库',
        f'{PREFIX}声骸',
    )
)
async def send_echo_list_msg(bot: Bot, ev: Event):
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    # 更新groupid
    await WavesBind.insert_waves_uid(user_id, ev.bot_id, uid, ev.group_id, lenth_limit=9)

    #
    im = await get_draw_list(ev, uid)
    return await bot.send(im)
