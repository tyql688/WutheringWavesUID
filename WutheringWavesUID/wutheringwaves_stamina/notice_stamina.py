from typing import Dict, List, Union

from gsuid_core.segment import MessageSegment

from ..utils.api.model import DailyData
from ..utils.database.models import WavesPush, WavesUser
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import PREFIX, WutheringWavesConfig


async def get_notice_list() -> Dict[str, Dict[str, Dict]]:
    """获取推送列表"""
    if not WutheringWavesConfig.get_config("StaminaPush").data:
        return {}

    msg_dict = {"private_msg_dict": {}, "group_msg_dict": {}}

    user_list: List[WavesUser] = await WavesUser.get_all_push_user_list()
    for user in user_list:
        if not user.uid or not user.cookie or user.status or not user.bot_id:
            continue

        push_data = await WavesPush.select_data_by_uid(user.uid)
        if push_data is None:
            continue

        await all_check(push_data.__dict__, msg_dict, user)

    return msg_dict


async def all_check(
    push_data: Dict, msg_dict: Dict[str, Dict[str, Dict]], user: WavesUser
):
    # 检查条件
    mode = "resin"

    bot_id = user.bot_id
    uid = user.uid

    succ, daily_info = await waves_api.get_daily_info(user.cookie)
    if not succ:
        await WavesUser.mark_invalid(user.cookie, "无效")
        notice_msg = [
            MessageSegment.text(f"❌[鸣潮] 特征码: {user.uid}\n"),
            MessageSegment.text("您的登录状态已失效\n"),
            MessageSegment.text(f"请使用命令【{PREFIX}登录】进行登录\n"),
        ]
        await save_push_data(mode, notice_msg, push_data, msg_dict, user)
        return

    # 体力数据
    daily_info = DailyData.model_validate(daily_info)

    _check = await check(
        mode,
        daily_info,
        push_data[f"{mode}_value"],
    )

    if push_data[f"{mode}_is_push"] == "on":
        if not WutheringWavesConfig.get_config("CrazyNotice").data:
            if not _check:
                await WavesPush.update_data_by_uid(
                    uid=uid, bot_id=bot_id, **{f"{mode}_is_push": "off"}
                )
            return

    # 准备推送
    if _check:
        if push_data[f"{mode}_push"] == "off":
            pass
        else:
            notice = "🌜你的结晶波片达到设定阈值啦！"
            if isinstance(_check, int):
                notice += f"（当前值: {_check}）"

            msg_list = [
                MessageSegment.text("✅[鸣潮] 推送提醒:\n"),
                MessageSegment.text(notice),
                MessageSegment.text(
                    f"\n可发送[{PREFIX}mr]或者[{PREFIX}每日]来查看更多信息！\n"
                ),
            ]

            await save_push_data(mode, msg_list, push_data, msg_dict, user, True)


async def check(
    mode: str,
    data: DailyData,
    limit: int,
) -> Union[bool, int]:
    if mode == "resin":
        if data.energyData.cur >= limit or data.energyData.cur >= data.energyData.total:
            return data.energyData.cur
        else:
            return False

    return False


async def save_push_data(
    mode: str,
    msg_list: List,
    push_data: Dict,
    msg_dict: Dict[str, Dict[str, Dict]],
    user: WavesUser,
    is_need_save: bool = False,
):
    # 获取数据
    bot_id = user.bot_id
    qid = user.user_id
    uid = user.uid

    private_msgs: Dict = msg_dict["private_msg_dict"]
    group_data: Dict = msg_dict["group_msg_dict"]

    # on 推送到私聊
    if push_data[f"{mode}_push"] == "on":
        # 添加私聊信息
        if qid not in private_msgs:
            private_msgs[qid] = []

        private_msgs[qid].append({"bot_id": bot_id, "messages": msg_list})
    # 群号推送到群聊
    else:
        # 初始化
        gid = push_data[f"{mode}_push"]
        if gid not in group_data:
            group_data[gid] = []
        msg_list.append(MessageSegment.at(qid))
        group_data[gid].append({"bot_id": bot_id, "messages": msg_list})

    if is_need_save:
        await WavesPush.update_data_by_uid(
            uid=uid, bot_id=bot_id, **{f"{mode}_is_push": "on"}
        )
