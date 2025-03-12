from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .draw_role_info import draw_role_img
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_102, WAVES_CODE_103
from ..utils.hint import error_reply
from ..utils.waves_api import waves_api

waves_role_info = SV("waves查询信息")


@waves_role_info.on_fullmatch((f"查询", f"卡片"), block=True)
async def send_role_info(bot: Bot, ev: Event):
    logger.info("[鸣潮]开始执行[查询信息]")
    user_id = ev.at if ev.at else ev.user_id
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    logger.info(f"[鸣潮][查询信息] user_id: {user_id} UID: {uid}")
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    ck = await waves_api.get_ck(uid, user_id)
    if not ck and not waves_api.is_net(uid):
        return await bot.send(error_reply(WAVES_CODE_102))

    im = await draw_role_img(uid, ck, ev)
    await bot.send(im)
