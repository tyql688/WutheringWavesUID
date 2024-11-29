from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.boardcast.send_msg import send_board_cast_msg
from .main import do_task, auto_bbs_task, do_sign_task
from ..wutheringwaves_config import PREFIX, WutheringWavesConfig

waves_bbs = SV(f'waves库街区任务')
sv_waves_sign = SV('鸣潮库街区签到+社区签到', priority=10)
waves_bbs_all = SV('鸣潮库街区签到配置', pm=1)
SIGN_TIME = WutheringWavesConfig.get_config('BBSSignTime').data
IS_REPORT = WutheringWavesConfig.get_config('PrivateSignReport').data


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


@waves_bbs_all.on_fullmatch((f'{PREFIX}att'))
async def bbs_recheck(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[全部社区签到]')
    await bot.send('[鸣潮] [全部社区签到] 已开始执行!')
    result = await auto_bbs_task()
    if not IS_REPORT:
        result['private_msg_dict'] = {}
    await send_board_cast_msg(result)
    await bot.send('[鸣潮] [全部社区签到] 执行完成!')


@scheduler.scheduled_job('cron', hour=SIGN_TIME[0], minute=SIGN_TIME[1])
async def waves_auto_bbs_task():
    if WutheringWavesConfig.get_config('BBSSchedSignin').data:
        logger.info('[鸣潮] [定时社区签到] 开始执行!')
        result = await auto_bbs_task()
        if not IS_REPORT:
            result['private_msg_dict'] = {}
        await send_board_cast_msg(result)


@sv_waves_sign.on_fullmatch(f'{PREFIX}签到', block=True)
async def get_sign_func(bot: Bot, ev: Event):
    msg = await do_sign_task(bot, ev)
    return await bot.send(msg)
