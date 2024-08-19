from typing import Dict, List, Union

from gsuid_core.gss import gss
from gsuid_core.logger import logger
from ..utils.api.model import DailyData
from ..utils.database.models import WavesUser, WavesPush
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import WutheringWavesConfig

NOTICE = {
    'resin': '🌜你的结晶波片达到设定阈值啦！',
}


async def get_notice_list() -> Dict[str, Dict[str, Dict]]:
    msg_dict = {}
    for bot_id in gss.active_bot:
        user_list: List[WavesUser] = await WavesUser.get_all_push_user_list()
        for user in user_list:
            if not user.uid or not user.cookie or user.status or not user.bot_id:
                continue

            push_data = await WavesPush.select_data_by_uid(user.uid)
            if push_data is None:
                continue

            succ, daily_info = await waves_api.get_daily_info(user.cookie)
            if not succ:
                await WavesUser.mark_invalid(user.cookie, '无效')
                try:
                    await gss.active_bot[bot_id].target_send(
                        f'❌ 鸣潮账号: {user.uid}\n'
                        f'您的ck已失效，请重新绑定ck\n', 'direct', user.user_id, user.bot_id, '', '')
                except Exception as e:
                    logger.error(f'[鸣潮推送提醒]推送{user.uid}数据失败! {e}')
                continue

            daily_info = DailyData(**daily_info)

            msg_dict = await all_check(
                user.bot_id,
                daily_info,
                push_data.__dict__,
                msg_dict,
                user.user_id,
                user.uid,
            )

    return msg_dict


async def all_check(
    bot_id: str,
    raw_data: DailyData,
    push_data: Dict,
    msg_dict: Dict[str, Dict[str, Dict]],
    user_id: str,
    uid: str,
) -> Dict[str, Dict[str, Dict]]:
    for mode in NOTICE.keys():
        _check = await check(
            mode,
            raw_data,
            push_data[f'{mode}_value'],
        )

        # 检查条件
        if push_data[f'{mode}_is_push'] == 'on':
            if not WutheringWavesConfig.get_config('CrazyNotice').data:
                if not _check:
                    await WavesPush.update_data_by_uid(
                        uid=uid, bot_id=bot_id, **{f'{mode}_is_push': 'off'}
                    )
                continue

        # 准备推送
        if _check:
            if push_data[f'{mode}_push'] == 'off':
                pass
            else:
                notice = NOTICE[mode]
                if isinstance(_check, int):
                    notice += f'（当前值: {_check}）'

                if bot_id not in msg_dict:
                    msg_dict[bot_id] = {'direct': {}, 'group': {}}
                    direct_data = msg_dict[bot_id]['direct']
                    group_data = msg_dict[bot_id]['group']

                # on 推送到私聊
                if push_data[f'{mode}_push'] == 'on':
                    # 添加私聊信息
                    if user_id not in direct_data:
                        direct_data[user_id] = notice
                    else:
                        direct_data[user_id] += notice
                # 群号推送到群聊
                else:
                    # 初始化
                    gid = push_data[f'{mode}_push']
                    if gid not in group_data:
                        group_data[gid] = {}

                    if user_id not in group_data[gid]:
                        group_data[gid][user_id] = notice
                    else:
                        group_data[gid][user_id] += notice

                await WavesPush.update_data_by_uid(
                    uid=uid, bot_id=bot_id, **{f'{mode}_is_push': 'on'}
                )
    return msg_dict


async def check(
    mode: str,
    data: DailyData,
    limit: int,
) -> Union[bool, int]:
    if mode == 'resin':
        if data.energyData.cur >= limit or data.energyData.cur >= data.energyData.total:
            return data.energyData.cur
        else:
            return False

    return False
