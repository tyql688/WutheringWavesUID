from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.at_help import ruser_id
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from .draw_char_list import draw_char_list_img

sv_waves_char_list = SV("ww角色练度统计")


@sv_waves_char_list.on_fullmatch(
    (
        "练度",
        "练度统计",
        "角色列表",
        "刷新练度",
        "刷新练度统计",
        "刷新角色列表",
    )
)
async def send_char_list_msg(bot: Bot, ev: Event):
    user_id = ruser_id(ev)
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    logger.info(f"[鸣潮] [练度统计] UID: {uid}")
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    # 更新groupid
    await WavesBind.insert_waves_uid(
        user_id, ev.bot_id, uid, ev.group_id, lenth_limit=9
    )

    im = await draw_char_list_img(uid, ev, user_id)
    return await bot.send(im)
