from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .main import do_task
from ..wutheringwaves_config import PREFIX

waves_bbs = SV(f'waves库街区任务')


@waves_bbs.on_fullmatch(
    (
        f'{PREFIX}社区签到',
        f'{PREFIX}社区任务',
        f'{PREFIX}每日任务',
        f'{PREFIX}库街区签到',
        f'{PREFIX}库街区任务',
        f'{PREFIX}tt',
    )
)
async def bbs_task(bot: Bot, ev: Event):
    msg = await do_task(bot, ev)
    return await bot.send(msg)
