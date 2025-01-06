from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .main import do_sign_task, auto_sign_task, auto_bbs_sign_task

from ..wutheringwaves_config import PREFIX, WutheringWavesConfig

sv_waves_sign = SV('鸣潮-签到', priority=1)
waves_sign_all = SV('鸣潮-全部签到', pm=1)
SIGN_TIME = WutheringWavesConfig.get_config('SignTime').data


@sv_waves_sign.on_fullmatch(f'{PREFIX}签到', block=True)
async def get_sign_func(bot: Bot, ev: Event):
    msg = await do_sign_task(bot, ev)
    return await bot.send(msg)


@scheduler.scheduled_job('cron', hour=SIGN_TIME[0], minute=SIGN_TIME[1])
async def waves_auto_new_sign_task():
    await auto_sign_task()


@waves_sign_all.on_fullmatch((f'{PREFIX}全部签到'))
async def sign_recheck_all(bot: Bot, ev: Event):
    await bot.send('[鸣潮] [全部签到] 已开始执行!')
    await auto_sign_task()
    await bot.send('[鸣潮] [全部签到] 执行完成!')


@waves_sign_all.on_fullmatch((f'{PREFIX}全部社区签到'))
async def sign_recheck_all(bot: Bot, ev: Event):
    await bot.send('[鸣潮] [全部社区签到] 已开始执行!')
    await auto_bbs_sign_task()
    await bot.send('[鸣潮] [全部社区签到] 执行完成!')
