from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.boardcast.send_msg import send_board_cast_msg
from .sign import sign_in, daily_sign

from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_103, WAVES_CODE_102
from ..utils.waves_prefix import PREFIX
from ..wutheringwaves_config.wutheringwaves_config import WutheringWavesConfig

sv_waves_sign = SV('鸣潮库街区签到')
sv_waves_sign_config = SV('鸣潮库街区签到配置', pm=1)

SIGN_TIME = WutheringWavesConfig.get_config('SignTime').data
IS_REPORT = WutheringWavesConfig.get_config('PrivateSignReport').data


@sv_waves_sign.on_fullmatch(f'{PREFIX}签到')
async def get_sign_func(bot: Bot, ev: Event):
    logger.info(f'[鸣潮] [签到] 用户: {ev.user_id}')
    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if not uid_list:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])
    res = []
    for uid in uid_list:
        ck = await WavesUser.get_user_cookie_by_uid(uid)
        if not ck:
            continue
        logger.info(f'[鸣潮] [签到] UID: {uid}')
        res.append(await sign_in(uid, ck))
    if not res:
        return await bot.send(ERROR_CODE[WAVES_CODE_102])
    await bot.send('\n'.join(res))


@sv_waves_sign_config.on_fullmatch(f'{PREFIX}全部重签')
async def recheck(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[全部重签]')
    await bot.send('[鸣潮] [全部重签] 已开始执行!')
    result = await daily_sign()
    if not IS_REPORT:
        result['private_msg_dict'] = {}
    await send_board_cast_msg(result)
    await bot.send('[鸣潮] [全部重签] 执行完成!')


# 定时任务-鸣潮签到
@scheduler.scheduled_job('cron', hour=SIGN_TIME[0], minute=SIGN_TIME[1])
async def waves_sign_at_night():
    if WutheringWavesConfig.get_config('SchedSignin').data:
        logger.info('[鸣潮] [定时签到] 开始执行!')
        result = await daily_sign()
        if not IS_REPORT:
            result['private_msg_dict'] = {}
        await send_board_cast_msg(result)
