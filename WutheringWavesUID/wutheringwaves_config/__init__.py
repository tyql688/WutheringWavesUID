import re

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .set_config import set_config_func, set_push_value
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


@sv_self_config.on_prefix(f'{PREFIX}设置')
async def send_config_ev(bot: Bot, ev: Event):
    logger.info('开始执行[设置阈值信息]')
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if uid is None:
        return await bot.send(f"您还未绑定鸣潮id, 请使用 {PREFIX}绑定UID 完成绑定！")

    func = ''.join(re.findall('[\u4e00-\u9fa5]', ev.text.replace('阈值', '')))
    value = re.findall(r'\d+', ev.text)
    value = value[0] if value else None

    if value is None:
        return await bot.send('请输入正确的阈值数字...')

    logger.info('[设置阈值信息]func: {}, value: {}'.format(func, value))
    im = await set_push_value(ev.bot_id, func, uid, int(value))
    await bot.send(im)
