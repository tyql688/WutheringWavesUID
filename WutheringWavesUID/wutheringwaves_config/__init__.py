from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .set_config import set_config_func
from .wutheringwaves_config import WutheringWavesConfig
from ..utils.database.models import WavesBind

sv_self_config = SV('鸣潮配置')

PREFIX = WutheringWavesConfig.get_config('WavesPrefix').data


@sv_self_config.on_prefix((f'{PREFIX}开启', f'{PREFIX}关闭'))
async def open_switch_func(bot: Bot, ev: Event):
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if uid is None:
        return await bot.send(f"您还未绑定鸣潮id, 请使用 {PREFIX}绑定UID 完成绑定！")

    logger.info(f"[{ev.user_id}]尝试[{ev.command[2:]}]了[{ev.text}]功能")

    im = await set_config_func(ev, uid)
    await bot.send(im)
