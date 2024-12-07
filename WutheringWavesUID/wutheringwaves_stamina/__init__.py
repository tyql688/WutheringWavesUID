import asyncio

from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.gss import gss
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV
from .draw_waves_stamina import draw_stamina_img
from .notice_stamina import get_notice_list
from ..utils.database.models import WavesBind
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_103
from ..utils.waves_prefix import PREFIX

waves_daily_info = SV('waves查询体力')


@waves_daily_info.on_fullmatch(
    (
        f'{PREFIX}每日',
        f'{PREFIX}mr',
        f'{PREFIX}实时便笺',
        f'{PREFIX}便笺',
        f'{PREFIX}便签',
        f'{PREFIX}体力',
    )
)
async def send_daily_info_pic(bot: Bot, ev: Event):
    await bot.logger.info(f'[鸣潮]开始执行[每日信息]: {ev.user_id}')
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])
    return await bot.send(await draw_stamina_img(bot, ev))


@scheduler.scheduled_job('cron', minute='*/10')
async def waves_daily_info_notice_job():
    result = await get_notice_list()
    logger.debug(f"鸣潮推送开始：{result}")
    # 执行私聊推送
    for bot_id in result:
        for BOT_ID in gss.active_bot:
            bot = gss.active_bot[BOT_ID]
            for user_id in result[bot_id]['direct']:
                msg_list = [MessageSegment.text('✅[鸣潮] 推送提醒:\n'),
                            MessageSegment.text(result[bot_id]['direct'][user_id])]

                await bot.target_send(msg_list, 'direct', user_id, bot_id, '', '')
                await asyncio.sleep(0.5)
            logger.info('[推送检查] 私聊推送完成')
            for gid in result[bot_id]['group']:
                msg_list = [MessageSegment.text('✅[鸣潮] 推送提醒:\n')]
                for user_id in result[bot_id]['group'][gid]:
                    msg_list.append(MessageSegment.at(user_id))
                    msg = result[bot_id]['group'][gid][user_id]
                    msg_list.append(MessageSegment.text(msg))

                msg_list.append(MessageSegment.text(f'\n可发送[{PREFIX}mr]或者[{PREFIX}每日]来查看更多信息！\n'))
                await bot.target_send(msg_list, 'group', gid, bot_id, '', '')
                await asyncio.sleep(0.5)
            logger.info('[推送检查] 群聊推送完成')
