from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.sv import SV

from ..wutheringwaves_config import WutheringWavesConfig
from .new_sign import auto_sign_task, sign_up_handler

sv_waves_sign = SV("鸣潮-签到", priority=1)
waves_sign_all = SV("鸣潮-全部签到", pm=1)
SIGN_TIME = WutheringWavesConfig.get_config("SignTime").data

task_name_sign_result = "订阅签到结果"


@sv_waves_sign.on_fullmatch(
    ("签到", "社区签到", "每日任务", "社区任务", "库街区签到"), block=True
)
async def get_sign_func(bot: Bot, ev: Event):
    msg = await sign_up_handler(bot, ev)
    return await bot.send(msg)


@scheduler.scheduled_job("cron", hour=SIGN_TIME[0], minute=SIGN_TIME[1])
async def waves_auto_new_sign_task():
    msg = await auto_sign_task()
    subscribes = await gs_subscribe.get_subscribe(task_name_sign_result)
    if subscribes:
        logger.info(f"[鸣潮]推送主人签到结果: {msg}")
        for sub in subscribes:
            await sub.send(msg)


@waves_sign_all.on_fullmatch(("全部签到"))
async def sign_recheck_all(bot: Bot, ev: Event):
    await bot.send("[鸣潮] [全部签到] 已开始执行!")
    msg = await auto_sign_task()
    await bot.send("[鸣潮] [全部签到] 执行完成!")
    await bot.send(msg)

    # subscribes = await gs_subscribe.get_subscribe(task_name_sign_result)
    # if subscribes:
    #     logger.info(f'[鸣潮]推送主人签到结果: {msg}')
    #     for sub in subscribes:
    #         await sub.send(msg)


@waves_sign_all.on_regex(("^(订阅|取消订阅)签到结果$"))
async def sign_sign_result(bot: Bot, ev: Event):
    if "取消" in ev.raw_text:
        option = "关闭"
    else:
        option = "开启"

    if option == "关闭":
        await gs_subscribe.delete_subscribe("single", task_name_sign_result, ev)
    else:
        await gs_subscribe.add_subscribe("single", task_name_sign_result, ev)

    await bot.send(f"[鸣潮] [订阅签到结果] 已{option}订阅!")
