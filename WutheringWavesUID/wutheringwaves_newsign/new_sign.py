import asyncio
import random
from typing import Dict, List, Literal

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.boardcast.models import BoardCastMsg, BoardCastMsgDict

from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_102
from ..utils.waves_api import waves_api
from ..utils.waves_send_msg import send_board_cast_msg
from ..wutheringwaves_config import WutheringWavesConfig
from .main import (
    create_sign_info_image,
    do_single_task,
    get_sign_interval,
    sign_in,
    single_daily_sign,
    single_task,
)

SIGN_STATUS = {
    True: "✅ 已完成",
    False: "❌ 未完成",
}


async def get_signin_config():
    from ..wutheringwaves_config import WutheringWavesConfig

    return WutheringWavesConfig.get_config("UserSchedSignin").data


async def get_bbs_signin_config():
    from ..wutheringwaves_config import WutheringWavesConfig

    return WutheringWavesConfig.get_config("UserBBSSchedSignin").data


async def sign_up_handler(bot: Bot, ev: Event):
    if not await get_signin_config() and not await get_bbs_signin_config():
        return "签到功能未开启"

    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return ERROR_CODE[WAVES_CODE_102]

    to_msg = {}
    expire_uid = []
    for uid in uid_list:
        msg_temp = {
            "signed": False,
            "bbs_signed": False,
        }
        token = await waves_api.get_self_waves_ck(uid, ev.user_id)
        if not token:
            if token == "":
                expire_uid.append(uid)
            continue

        # 签到状态
        signed = False
        if await get_signin_config():
            sign_res = await waves_api.sign_in_task_list(uid, token)
            if isinstance(sign_res, dict):
                signed = sign_res.get("data", {}).get("isSigIn", False)

            if not signed:
                res = await sign_in(uid, token)
                if "成功" in res:
                    signed = True

        msg_temp["signed"] = signed

        bbs_signed = False
        if await get_bbs_signin_config():
            bbs_signed = await do_single_task(uid, token)
            if isinstance(bbs_signed, dict) and all(bbs_signed.values()):
                bbs_signed = True
            elif isinstance(bbs_signed, bool):
                pass
            else:
                bbs_signed = False

        msg_temp["bbs_signed"] = bbs_signed

        to_msg[uid] = msg_temp

        await asyncio.sleep(random.randint(1, 2))

    if not to_msg:
        return ERROR_CODE[WAVES_CODE_102]

    msg_list = []

    for uid, msg in to_msg.items():
        msg_list.append(f"特征码: {uid}")
        if await get_signin_config():
            msg_list.append(f"签到状态: {SIGN_STATUS[msg['signed']]}")
        else:
            msg_list.append("签到状态: 功能未开启")
        if await get_bbs_signin_config():
            msg_list.append(f"社区签到状态: {SIGN_STATUS[msg['bbs_signed']]}")
        else:
            msg_list.append("社区签到状态: 功能未开启")

        msg_list.append("-----------------------------")

    for uid in expire_uid:
        msg_list.append(f"失效特征码: {uid}")

    return "\n".join(msg_list)


async def auto_sign_task():

    need_user_list: List[WavesUser] = []
    bbs_user = set()
    sign_user = set()
    if (
        WutheringWavesConfig.get_config("BBSSchedSignin").data
        or WutheringWavesConfig.get_config("SchedSignin").data
    ):
        _user_list: List[WavesUser] = await WavesUser.get_waves_all_user2()
        for user in _user_list:
            _uid = user.user_id
            if not _uid:
                continue

            if WutheringWavesConfig.get_config("SigninMaster").data:
                # 如果 SigninMaster 为 True，添加到 user_list 中
                need_user_list.append(user)
                bbs_user.add(user.uid)
                sign_user.add(user.uid)
                continue

            is_need = False
            if user.bbs_sign_switch != "off":
                # 如果 bbs_sign_switch 不为 'off'，添加到 user_list 中
                bbs_user.add(user.uid)
                is_need = True

            if user.sign_switch != "off":
                # 如果 sign_switch 不为 'off'，添加到 user_list 中
                sign_user.add(user.uid)
                is_need = True

            if is_need:
                need_user_list.append(user)

    private_sign_msgs = {}
    group_sign_msgs = {}
    all_sign_msgs = {"failed": 0, "success": 0}

    private_bbs_msgs = {}
    group_bbs_msgs = {}
    all_bbs_msgs = {"failed": 0, "success": 0}

    async def process_user(semaphore, user: WavesUser):
        async with semaphore:
            if user.cookie == "":
                return
            if user.status:
                return

            succ, data = await waves_api.refresh_data(user.uid, user.cookie)
            if not succ:
                if "封禁" in data:
                    raise Exception(f"自动签到失败: {data}")
                logger.warning(f"自动签到数据刷新失败: {user.uid} {data}")
                return

            await asyncio.sleep(random.randint(1, 2))

            if (
                WutheringWavesConfig.get_config("SchedSignin").data
                and user.uid in sign_user
            ) or WutheringWavesConfig.get_config("SigninMaster").data:
                await single_daily_sign(
                    user.bot_id,
                    user.uid,
                    user.sign_switch,
                    user.user_id,
                    user.cookie,
                    private_sign_msgs,
                    group_sign_msgs,
                    all_sign_msgs,
                )

                await asyncio.sleep(random.randint(1, 2))

            if (
                WutheringWavesConfig.get_config("BBSSchedSignin").data
                and user.uid in bbs_user
            ) or WutheringWavesConfig.get_config("SigninMaster").data:
                await single_task(
                    user.bot_id,
                    user.uid,
                    user.bbs_sign_switch,
                    user.user_id,
                    user.cookie,
                    private_bbs_msgs,
                    group_bbs_msgs,
                    all_bbs_msgs,
                )

                await asyncio.sleep(random.randint(2, 4))

    max_concurrent: int = WutheringWavesConfig.get_config("SigninConcurrentNum2").data
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [process_user(semaphore, user) for user in need_user_list]
    for i in range(0, len(tasks), max_concurrent):
        batch = tasks[i : i + max_concurrent]
        results = await asyncio.gather(*batch, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                return f"{result.args[0]}"

        delay = round(await get_sign_interval(), 2)
        logger.info(f"[鸣潮] [自动签到] 等待{delay:.2f}秒进行下一次签到")
        await asyncio.sleep(delay)

    sign_result = await to_board_cast_msg(
        private_sign_msgs, group_sign_msgs, "游戏签到", theme="blue"
    )
    if not WutheringWavesConfig.get_config("PrivateSignReport").data:
        sign_result["private_msg_dict"] = {}
    if not WutheringWavesConfig.get_config("GroupSignReport").data:
        sign_result["group_msg_dict"] = {}
    await send_board_cast_msg(sign_result, "sign")

    bbs_result = await to_board_cast_msg(
        private_bbs_msgs, group_bbs_msgs, "社区签到", theme="yellow"
    )
    if not WutheringWavesConfig.get_config("PrivateSignReport").data:
        bbs_result["private_msg_dict"] = {}
    if not WutheringWavesConfig.get_config("GroupSignReport").data:
        bbs_result["group_msg_dict"] = {}
    await send_board_cast_msg(bbs_result, "sign")

    return f"[鸣潮]自动任务\n今日成功游戏签到 {all_sign_msgs['success']} 个账号\n今日社区签到 {all_bbs_msgs['success']} 个账号"


async def to_board_cast_msg(
    private_msgs,
    group_msgs,
    type: Literal["社区签到", "游戏签到"] = "社区签到",
    theme: str = "yellow",
):
    # 转为广播消息
    private_msg_dict: Dict[str, List[BoardCastMsg]] = {}
    group_msg_dict: Dict[str, BoardCastMsg] = {}
    for qid in private_msgs:
        msgs = []
        for i in private_msgs[qid]:
            msgs.extend(i["msg"])

        if qid not in private_msg_dict:
            private_msg_dict[qid] = []

        private_msg_dict[qid].append(
            {
                "bot_id": private_msgs[qid][0]["bot_id"],
                "messages": msgs,
            }
        )

    failed_num = 0
    success_num = 0
    for gid in group_msgs:
        success = group_msgs[gid]["success"]
        faild = group_msgs[gid]["failed"]
        success_num += int(success)
        failed_num += int(faild)
        title = f"✅[鸣潮]今日{type}任务已完成！\n本群共签到成功{success}人\n共签到失败{faild}人"
        messages = []
        if WutheringWavesConfig.get_config("GroupSignReportPic").data:
            image = create_sign_info_image(title, theme="yellow")
            messages.append(MessageSegment.image(image))
        else:
            messages.append(MessageSegment.text(title))
        if group_msgs[gid]["push_message"]:
            messages.append(MessageSegment.text("\n"))
            messages.extend(group_msgs[gid]["push_message"])
        group_msg_dict[gid] = {
            "bot_id": group_msgs[gid]["bot_id"],
            "messages": messages,
        }

    result: BoardCastMsgDict = {
        "private_msg_dict": private_msg_dict,
        "group_msg_dict": group_msg_dict,
    }
    return result
