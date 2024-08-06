import asyncio
import random
from typing import Dict, List

from gsuid_core.logger import logger
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.boardcast.models import BoardCastMsg, BoardCastMsgDict
from ..utils.api.model import DailyData
from ..utils.database.models import WavesUser
from ..utils.error_reply import WAVES_CODE_101, ERROR_CODE
from ..utils.waves_api import waves_api


async def sign_in(uid: str, ck: str) -> str:
    sign_title = f'[鸣潮] [签到]'

    succ, daily_info = await waves_api.get_daily_info(ck)
    if not succ:
        # 检查ck
        return f'{sign_title} UID{uid} {ERROR_CODE[WAVES_CODE_101]}'

    daily_info = DailyData(**daily_info)
    if daily_info.hasSignIn:
        # 已经签到
        logger.info(f'{sign_title} UID{uid} 该用户今日已签到,跳过...')
        return f'{sign_title} UID{uid} 今日已签到！'

    sign_in_res = await waves_api.sign_in(daily_info.serverId, daily_info.roleId, ck)
    if isinstance(sign_in_res, dict):
        if sign_in_res.get('code') == 200 and sign_in_res.get('data'):
            # 签到成功
            return f'{sign_title} UID{uid} 签到成功！'
        elif sign_in_res.get('code') == 1511:
            # 已经签到
            logger.info(f'{sign_title} {uid} 该用户今日已签到,跳过...')
            return f'{sign_title} UID{uid} 今日已签到！'
    # 签到失败
    return f'{sign_title} UID{uid} 签到失败！'


async def single_daily_sign(
        bot_id: str,
        uid: str,
        gid: str,
        qid: str,
        ck: str,
        private_msgs: Dict,
        group_msgs: Dict,
):
    im = await sign_in(uid, ck)
    if gid == 'on':
        if qid not in private_msgs:
            private_msgs[qid] = []
        private_msgs[qid].append(
            {'bot_id': bot_id, 'uid': uid, 'msg': [MessageSegment.text(im)]}
        )
    else:
        # 向群消息推送列表添加这个群
        if gid not in group_msgs:
            group_msgs[gid] = {
                'bot_id': bot_id,
                'success': 0,
                'failed': 0,
                'push_message': '',
            }
        if im.startswith(('签到失败', '网络有点忙', 'OK', 'ok')):
            group_msgs[gid]['failed'] += 1
            group_msgs[gid]['push_message'].extend(
                [
                    MessageSegment.text('\n'),
                    MessageSegment.at(qid),
                    MessageSegment.text(im),
                ]
            )
        else:
            group_msgs[gid]['success'] += 1


async def daily_sign():
    tasks = []
    private_msgs = {}
    group_msgs = {}
    _user_list: List[WavesUser] = await WavesUser.get_all_user()
    uid_list = []
    user_list: List[WavesUser] = []
    for user in _user_list:
        _uid = user.user_id
        _switch = user.sign_switch
        if _switch != 'off' and not user.status and _uid:
            uid_list.append(_uid)
            user_list.append(user)

    logger.info(f'[鸣潮] [全部重签] [UID列表] {uid_list}')
    for user in user_list:
        tasks.append(
            single_daily_sign(
                user.bot_id,
                user.uid,
                user.sign_switch,
                user.user_id,
                user.cookie,
                private_msgs,
                group_msgs,
            )
        )
        if len(tasks) >= 1:
            await asyncio.gather(*tasks)
            delay = 30 + random.randint(3, 35)
            logger.info(
                f'[{game_name}] [签到] 已签到{len(tasks)}个用户, 等待{delay}秒进行下一次签到'
            )
            tasks.clear()
            await asyncio.sleep(delay)
    await asyncio.gather(*tasks)
    tasks.clear()

    # 转为广播消息
    private_msg_dict: Dict[str, List[BoardCastMsg]] = {}
    group_msg_dict: Dict[str, BoardCastMsg] = {}
    for qid in private_msgs:
        msgs = []
        for i in private_msgs[qid]:
            msgs.extend(i['msg'])

        if qid not in private_msg_dict:
            private_msg_dict[qid] = []

        private_msg_dict[qid].append(
            {
                'bot_id': private_msgs[qid][0]['bot_id'],
                'messages': msgs,
            }
        )

    for gid in group_msgs:
        success = group_msgs[gid]['success']
        faild = group_msgs[gid]['failed']
        title = f'✅[鸣潮]今日自动签到已完成！\n📝本群共签到成功{success}人，共签到失败{faild}人。'
        messages = [MessageSegment.text(title)]
        if group_msgs[gid]['push_message']:
            messages.append(MessageSegment.text('\n'))
            messages.extend(group_msgs[gid]['push_message'])
        group_msg_dict[gid] = {
            'bot_id': group_msgs[gid]['bot_id'],
            'messages': messages,
        }

    result: BoardCastMsgDict = {
        'private_msg_dict': private_msg_dict,
        'group_msg_dict': group_msg_dict,
    }

    logger.info(result)
    return result
