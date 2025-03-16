import asyncio
import random
from typing import Dict, List

from PIL import Image, ImageDraw

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.boardcast.models import BoardCastMsg, BoardCastMsgDict

from ..utils.api.api import MAIN_URL
from ..utils.api.model import DailyData
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_101, WAVES_CODE_102
from ..utils.fonts.waves_fonts import waves_font_24
from ..utils.waves_api import waves_api
from ..utils.waves_send_msg import send_board_cast_msg
from ..wutheringwaves_config import WutheringWavesConfig
from .bbs_api import bbs_api

GET_GOLD_URL = f"{MAIN_URL}/encourage/gold/getTotalGold"
GET_TASK_URL = f"{MAIN_URL}/encourage/level/getTaskProcess"
FORUM_LIST_URL = f"{MAIN_URL}/forum/list"
LIKE_URL = f"{MAIN_URL}/forum/like"
SIGN_IN_URL = f"{MAIN_URL}/user/signIn"
POST_DETAIL_URL = f"{MAIN_URL}/forum/getPostDetail"
SHARE_URL = f"{MAIN_URL}/encourage/level/shareTask"


async def get_sign_interval(is_bbs: bool = False):
    next_group_sign_time = WutheringWavesConfig.get_config(
        "SigninConcurrentNumInterval"
    ).data
    ratio = random.uniform(1, 2) if is_bbs else 1
    if not next_group_sign_time:
        return random.uniform(2, 3) * ratio
    return (
        random.uniform(float(next_group_sign_time[0]), float(next_group_sign_time[1]))
        * ratio
    )


async def do_sign_in(taskData, uid, token, form_result):
    key = "用户签到"
    form_result[uid][key] = -1
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        form_result[uid][key] = taskData["needActionTimes"] - taskData["completeTimes"]
        return

    # 用户签到
    sign_in_res = await bbs_api.do_sign_in(token)
    if isinstance(sign_in_res, dict):
        if sign_in_res.get("code") == 200 and sign_in_res.get("data"):
            # 签到成功
            form_result[uid][key] = taskData["needActionTimes"]
            return
    logger.warning(f"[鸣潮][社区签到]签到失败 uid: {uid} sign_in_res: {sign_in_res}")


async def do_detail(taskData, uid, token, form_result, post_list):
    key = "浏览帖子"
    form_result[uid][key] = -1
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        form_result[uid][key] = taskData["needActionTimes"] - taskData["completeTimes"]
        return
    # 浏览帖子
    detail_succ = 0
    for i, post in enumerate(post_list):
        post_detail_res = await bbs_api.do_post_detail(token, post["postId"])
        if isinstance(post_detail_res, dict):
            if post_detail_res.get("code") == 200:
                detail_succ += 1
                # 浏览成功
                form_result[uid][key] = detail_succ
        if detail_succ >= taskData["needActionTimes"] - taskData["completeTimes"]:
            return

    logger.warning(f"[鸣潮][社区签到]浏览失败 uid: {uid}")


async def do_like(taskData, uid, token, form_result, post_list):
    key = "点赞帖子"
    form_result[uid][key] = -1
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        form_result[uid][key] = taskData["needActionTimes"] - taskData["completeTimes"]
        return

    # 用户点赞5次
    like_succ = 0
    for i, post in enumerate(post_list):
        like_res = await bbs_api.do_like(token, post["postId"], post["userId"])
        if isinstance(like_res, dict):
            if like_res.get("code") == 200:
                like_succ += 1
                # 点赞成功
                form_result[uid][key] = like_succ
        if like_succ >= taskData["needActionTimes"] - taskData["completeTimes"]:
            return

    logger.warning(f"[鸣潮][社区签到]点赞失败 uid: {uid}")


async def do_share(taskData, uid, token, form_result):
    key = "分享帖子"
    form_result[uid][key] = -1
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        form_result[uid][key] = taskData["needActionTimes"] - taskData["completeTimes"]
        return

    # 分享
    share_res = await bbs_api.do_share(token)
    if isinstance(share_res, dict):
        if share_res.get("code") == 200:
            # 分享成功
            form_result[uid][key] = taskData["needActionTimes"]
            return

    logger.exception(f"[鸣潮][社区签到]分享失败 uid: {uid}")


async def do_single_task(uid, token):
    # 任务列表
    task_res = await bbs_api.get_task(token)
    if not isinstance(task_res, dict):
        return
    if task_res.get("code") != 200 or not task_res.get("data"):
        return

        # check 1
    need_post_list_flag = False
    for i in task_res["data"]["dailyTask"]:
        if i["completeTimes"] == i["needActionTimes"]:
            continue
        if "签到" not in i["remark"] or "分享" not in i["remark"]:
            need_post_list_flag = True

    post_list = []
    if need_post_list_flag:
        # 获取帖子
        form_list_res = await bbs_api.get_form_list(token)
        if isinstance(form_list_res, dict):
            if form_list_res.get("code") == 200 and form_list_res.get("data"):
                # 获取到帖子列表
                post_list = form_list_res["data"]["postList"]
        if not post_list:
            logger.exception(
                f"[鸣潮][社区签到]获取帖子列表失败 uid: {uid} res: {form_list_res}"
            )
            # 未获取帖子列表
            return

    form_result = {
        uid: {
            "用户签到": "",
            "浏览帖子": "",
            "点赞帖子": "",
            "分享帖子": "",
            "库洛币": "",
        }
    }
    # 获取到任务列表
    for i in task_res["data"]["dailyTask"]:
        if "签到" in i["remark"]:
            await do_sign_in(i, uid, token, form_result)
        elif "浏览" in i["remark"]:
            await do_detail(i, uid, token, form_result, post_list)
        elif "点赞" in i["remark"]:
            await do_like(i, uid, token, form_result, post_list)
        elif "分享" in i["remark"]:
            await do_share(i, uid, token, form_result)

        await asyncio.sleep(random.uniform(0, 1))

    gold_res = await bbs_api.get_gold(token)
    if isinstance(gold_res, dict):
        if gold_res.get("code") == 200:
            form_result[uid]["库洛币"] = gold_res["data"]["goldNum"]

    return form_result


async def single_task(
    bot_id: str,
    uid: str,
    gid: str,
    qid: str,
    ck: str,
    private_msgs: Dict,
    group_msgs: Dict,
    all_msgs: Dict,
):
    im = await do_single_task(uid, ck)
    if not im:
        return
    msg = []
    msg.append(f"特征码: {uid}")
    for i, r in im[str(uid)].items():
        if r == 0:
            r = "今日已完成！"
        elif r == -1:
            r = "失败"
        else:
            if i == "用户签到":
                r = "签到成功"
            elif i == "浏览帖子":
                r = f"浏览帖子成功 {r} 次"
            elif i == "点赞帖子":
                r = f"点赞帖子成功 {r} 次"
            elif i == "分享帖子":
                r = f"分享帖子成功"
            elif i == "库洛币":
                r = f" 当前为{r}"

        msg.append(f"{i}: {r}")

    im = "\n".join(msg)
    if gid == "on":
        if qid not in private_msgs:
            private_msgs[qid] = []
        private_msgs[qid].append(
            {"bot_id": bot_id, "uid": uid, "msg": [MessageSegment.text(im)]}
        )
        if "失败" in im:
            all_msgs["failed"] += 1
        else:
            all_msgs["success"] += 1
    elif gid == "off":
        if "失败" in im:
            all_msgs["failed"] += 1
        else:
            all_msgs["success"] += 1
    else:
        # 向群消息推送列表添加这个群
        if gid not in group_msgs:
            group_msgs[gid] = {
                "bot_id": bot_id,
                "success": 0,
                "failed": 0,
                "push_message": [],
            }

        if "失败" in im:
            all_msgs["failed"] += 1
            group_msgs[gid]["failed"] += 1
            group_msgs[gid]["push_message"].extend(
                [
                    MessageSegment.text("\n"),
                    MessageSegment.at(qid),
                    MessageSegment.text(im),
                ]
            )
        else:
            all_msgs["success"] += 1
            group_msgs[gid]["success"] += 1


async def auto_sign_task():
    bbs_expiregid2uid = {}
    sign_expiregid2uid = {}
    bbs_user_list = []
    sign_user_list = []
    if (
        WutheringWavesConfig.get_config("BBSSchedSignin").data
        or WutheringWavesConfig.get_config("SchedSignin").data
    ):
        _user_list: List[WavesUser] = await WavesUser.get_waves_all_user2()
        logger.info(f"[鸣潮] [定时签到] 需要处理token总人数 {len(_user_list)}")
        (
            bbs_expiregid2uid,
            sign_expiregid2uid,
            bbs_user_list,
            sign_user_list,
        ) = await process_all_users(_user_list)

    sign_success = 0
    sign_fail = 0
    if WutheringWavesConfig.get_config("SchedSignin").data:
        logger.info(f"[鸣潮] [定时签到] 开始执行! 总人数: {len(sign_user_list)}")
        result, num = await daily_sign_action(sign_expiregid2uid, sign_user_list)
        if not WutheringWavesConfig.get_config("PrivateSignReport").data:
            result["private_msg_dict"] = {}
        if not WutheringWavesConfig.get_config("GroupSignReport").data:
            result["group_msg_dict"] = {}
        await send_board_cast_msg(result, "sign")
        sign_success = num["success_num"]
        sign_fail = num["failed_num"]

    bbs_success = 0
    bbs_fail = 0
    if WutheringWavesConfig.get_config("BBSSchedSignin").data:
        logger.info(f"[鸣潮] [定时社区签到] 开始执行! 总人数: {len(bbs_user_list)}")
        result, num = await auto_bbs_task_action(bbs_expiregid2uid, bbs_user_list)
        if not WutheringWavesConfig.get_config("PrivateSignReport").data:
            result["private_msg_dict"] = {}
        if not WutheringWavesConfig.get_config("GroupSignReport").data:
            result["group_msg_dict"] = {}
        await send_board_cast_msg(result, "sign")
        bbs_success = num["success_num"]
        bbs_fail = num["failed_num"]

    return f"[鸣潮]自动任务\n今日成功游戏签到 {sign_success} 个账号\n今日社区签到 {bbs_success} 个账号"


async def process_user(
    user, bbs_expiregid2uid, sign_expiregid2uid, bbs_user_list, sign_user_list
):
    _uid = user.user_id
    if not _uid:
        return
    # 异步调用 refresh_data
    succ, _ = await waves_api.refresh_data(user.uid, user.cookie)
    if not succ:
        # await WavesUser.mark_invalid(user.cookie, "无效")
        # 如果刷新数据失败，更新 expiregid2uid
        if user.bbs_sign_switch != "off":
            bbs_expiregid2uid.setdefault(user.bbs_sign_switch, []).append(user.user_id)
        if user.sign_switch != "off":
            sign_expiregid2uid.setdefault(user.sign_switch, []).append(user.user_id)
        return

    if WutheringWavesConfig.get_config("SigninMaster").data:
        # 如果 SigninMaster 为 True，添加到 user_list 中
        bbs_user_list.append(user)
        sign_user_list.append(user)
        return

    if user.bbs_sign_switch != "off":
        # 如果 bbs_sign_switch 不为 'off'，添加到 user_list 中
        bbs_user_list.append(user)

    if user.sign_switch != "off":
        # 如果 sign_switch 不为 'off'，添加到 user_list 中
        sign_user_list.append(user)


async def process_all_users(_user_list: List):
    bbs_expiregid2uid = {}
    sign_expiregid2uid = {}
    bbs_user_list = []
    sign_user_list = []

    # 定义每个批次的大小
    batch_size: int = WutheringWavesConfig.get_config("SigninConcurrentNum").data
    semaphore = asyncio.Semaphore(batch_size)
    batches = [
        _user_list[i : i + batch_size] for i in range(0, len(_user_list), batch_size)
    ]

    async def process_user_with_semaphore(user):
        async with semaphore:
            await process_user(
                user,
                bbs_expiregid2uid,
                sign_expiregid2uid,
                bbs_user_list,
                sign_user_list,
            )

    # 对每个批次创建异步任务列表并执行
    flag = 1
    for batch in batches:
        tasks = [process_user_with_semaphore(user) for user in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        delay = round(await get_sign_interval(), 2)
        logger.info(
            f"[鸣潮] [签到任务] 正在处理token验证批次[{flag}]，共{len(tasks)}个用户, 等待{delay:.2f}秒进行下一次token验证"
        )
        flag += 1
        await asyncio.sleep(delay)

    return bbs_expiregid2uid, sign_expiregid2uid, bbs_user_list, sign_user_list


async def auto_bbs_task_action(expiregid2uid, user_list):
    tasks = []
    private_msgs = {}
    group_msgs = {}
    all_msgs = {"failed": 0, "success": 0}

    async def process_user(semaphore, user):
        async with semaphore:
            return await single_task(
                user.bot_id,
                user.uid,
                user.bbs_sign_switch,
                user.user_id,
                user.cookie,
                private_msgs,
                group_msgs,
                all_msgs,
            )

    max_concurrent: int = WutheringWavesConfig.get_config("SigninConcurrentNum").data
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [process_user(semaphore, user) for user in user_list]
    for i in range(0, len(tasks), max_concurrent):
        batch = tasks[i : i + max_concurrent]
        results = await asyncio.gather(*batch, return_exceptions=True)

        delay = round(await get_sign_interval(), 2)
        logger.info(f"[鸣潮] [社区签到] 等待{delay:.2f}秒进行下一次签到")
        await asyncio.sleep(delay)

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
        title = f"✅[鸣潮]今日社区签到任务已完成！\n本群共签到成功{success}人\n共签到失败{faild}人\nToken过期{len(expiregid2uid.get(gid, []))}人"
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

    num = {
        "failed_num": all_msgs["failed"],
        "success_num": all_msgs["success"],
        "push_success_num": success_num,
        "push_failed_num": failed_num,
    }
    logger.info(f"自动社区签到结果: {num}")
    # logger.info(result)
    return result, num


async def single_daily_sign(
    bot_id: str,
    uid: str,
    gid: str,
    qid: str,
    ck: str,
    private_msgs: Dict,
    group_msgs: Dict,
    all_msgs: Dict,
):
    im = await sign_in(uid, ck)
    if gid == "on":
        if qid not in private_msgs:
            private_msgs[qid] = []
        private_msgs[qid].append(
            {"bot_id": bot_id, "uid": uid, "msg": [MessageSegment.text(im)]}
        )
        if "失败" in im:
            all_msgs["failed"] += 1
        else:
            all_msgs["success"] += 1
    elif gid == "off":
        if "失败" in im:
            all_msgs["failed"] += 1
        else:
            all_msgs["success"] += 1
    else:
        # 向群消息推送列表添加这个群
        if gid not in group_msgs:
            group_msgs[gid] = {
                "bot_id": bot_id,
                "success": 0,
                "failed": 0,
                "push_message": [],
            }
        if "失败" in im:
            all_msgs["failed"] += 1
            group_msgs[gid]["failed"] += 1
            group_msgs[gid]["push_message"].extend(
                [
                    MessageSegment.text("\n"),
                    MessageSegment.at(qid),
                    MessageSegment.text(im),
                ]
            )
        else:
            all_msgs["success"] += 1
            group_msgs[gid]["success"] += 1


async def daily_sign_action(expiregid2uid, user_list):
    tasks = []
    private_msgs = {}
    group_msgs = {}
    all_msgs = {"failed": 0, "success": 0}

    async def process_user(semaphore, user):
        async with semaphore:
            return await single_daily_sign(
                user.bot_id,
                user.uid,
                user.sign_switch,
                user.user_id,
                user.cookie,
                private_msgs,
                group_msgs,
                all_msgs,
            )

    max_concurrent: int = WutheringWavesConfig.get_config("SigninConcurrentNum").data
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [process_user(semaphore, user) for user in user_list]
    for i in range(0, len(tasks), max_concurrent):
        batch = tasks[i : i + max_concurrent]
        results = await asyncio.gather(*batch, return_exceptions=True)

        delay = round(await get_sign_interval(), 2)
        logger.info(f"[鸣潮] [签到]  等待{delay:.2f}秒进行下一次签到")
        await asyncio.sleep(delay)

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

    success_num = 0
    failed_num = 0
    for gid in group_msgs:
        success = group_msgs[gid]["success"]
        faild = group_msgs[gid]["failed"]
        failed_num += int(faild)
        success_num += int(success)
        title = f"✅[鸣潮]今日自动签到已完成！\n本群共签到成功{success}人\n共签到失败{faild}人\nToken过期{len(expiregid2uid.get(gid, []))}人"
        messages = []
        if WutheringWavesConfig.get_config("GroupSignReportPic").data:
            image = create_sign_info_image(title, theme="blue")
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

    num = {
        "failed_num": all_msgs["failed"],
        "success_num": all_msgs["success"],
        "push_success_num": success_num,
        "push_failed_num": failed_num,
    }
    logger.info(f"自动游戏签到结果: {num}")
    # logger.info(result)
    return result, num


async def do_sign_task(bot: Bot, ev: Event):
    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return ERROR_CODE[WAVES_CODE_102]
    # 进行校验UID是否绑定CK
    valid_ck_list = []

    expire_uid = []
    for uid in uid_list:
        ck = await waves_api.get_self_waves_ck(uid, ev.user_id)
        if not ck:
            if ck == "":
                expire_uid.append(uid)
            continue
        succ, _ = await waves_api.refresh_data(uid, ck)
        if not succ:
            expire_uid.append(uid)
            continue

        valid_ck_list.append((uid, ck))

    if len(valid_ck_list) == 0:
        return ERROR_CODE[WAVES_CODE_102]

    form_result = {}
    for uid, token in valid_ck_list:
        res = await do_single_task(uid, token)
        if res:
            form_result[uid] = res[uid]
        else:
            expire_uid.append(uid)
            continue

        res = await sign_in(uid, token)
        if res:
            if not isinstance(form_result[uid], dict):
                form_result[uid] = {}
            form_result[uid]["游戏签到"] = res

    msg_list = []
    for uid, temp in form_result.items():
        msg_list.append(f"账号 {uid} 签到结果")
        msg_list.append("")
        if "游戏签到" in temp:
            msg_list.append(f"======= 游戏签到 =======")
            msg_list.append(f"[游戏签到] {temp['游戏签到']}")
            temp.pop("游戏签到")
            msg_list.append("")

        msg_list.append("游戏签到已完成！")
        if len(temp) == 0:
            continue
        msg_list.append(f"======= 社区签到 =======")
        for title, value in temp.items():
            if value == 0:
                value = "今日已完成！"
            elif title == "用户签到":
                value = "签到成功"
            elif title == "浏览帖子":
                value = f"浏览帖子成功 {value} 次"
            elif title == "点赞帖子":
                value = f"点赞帖子成功 {value} 次"
            elif title == "分享帖子":
                value = f"分享帖子成功"
            elif title == "库洛币":
                value = f" 当前为{value}"

            msg_list.append(f"[{title}] {value}")

        msg_list.append("社区任务已完成！")
        msg_list.append("-----------------------------")

    for uid in expire_uid:
        msg_list.append(f"失效特征码: {uid}")

    return "\n".join(msg_list)


async def sign_in(uid: str, ck: str) -> str:
    succ, daily_info = await waves_api.get_daily_info(ck)
    if not succ:
        # 检查ck
        return f"签到失败！\n{ERROR_CODE[WAVES_CODE_101]}"

    daily_info = DailyData(**daily_info)
    if daily_info.hasSignIn:
        # 已经签到
        logger.debug(f"UID{uid} 该用户今日已签到,跳过...")
        return f"今日已签到！请勿重复签到！"

    sign_in_res = await waves_api.sign_in(daily_info.roleId, ck)
    if isinstance(sign_in_res, dict):
        if sign_in_res.get("code") == 200 and sign_in_res.get("data"):
            # 签到成功
            return f"签到成功！"
        elif sign_in_res.get("code") == 1511:
            # 已经签到
            logger.debug(f"UID{uid} 该用户今日已签到,跳过...")
            return f"今日已签到！请勿重复签到！"
    # 签到失败
    return f"签到失败！"


def create_gradient_background(width, height, start_color, end_color=(255, 255, 255)):
    """
    使用 PIL 创建渐变背景
    start_color: 起始颜色，如 (230, 230, 255) 浅蓝
    end_color: 结束颜色，默认白色
    """
    # 创建新图像
    image = Image.new("RGB", (width, height))

    for y in range(height):
        # 计算当前行的颜色比例
        ratio = y / height

        # 计算当前行的 RGB 值
        r = int(end_color[0] * ratio + start_color[0] * (1 - ratio))
        g = int(end_color[1] * ratio + start_color[1] * (1 - ratio))
        b = int(end_color[2] * ratio + start_color[2] * (1 - ratio))

        # 创建当前行的颜色
        line_color = (r, g, b)
        # 绘制当前行
        for x in range(width):
            image.putpixel((x, y), line_color)

    return image


def create_sign_info_image(text, theme="blue"):
    text = text[1:]
    # 创建图片
    width = 600
    height = 250  # 稍微减小高度使布局更紧凑

    # 预定义主题颜色
    themes = {
        "blue": (230, 230, 255),  # 浅蓝
        "yellow": (255, 255, 230),  # 浅黄
        "pink": (255, 230, 230),  # 浅粉
        "green": (230, 255, 230),  # 浅绿
    }

    # 获取主题颜色，默认浅蓝
    start_color = themes.get(theme, themes["blue"])

    # 创建渐变背景
    img = create_gradient_background(width, height, start_color)
    draw = ImageDraw.Draw(img)

    # 颜色定义
    title_color = (51, 51, 51)  # 标题色

    # 绘制装饰边框
    border_color = (200, 200, 200)
    draw.rectangle([(10, 10), (width - 10, height - 10)], outline=border_color, width=2)

    # 文本处理
    lines = text.split("\n")
    left_margin = 40  # 左边距
    y = 40  # 起始y坐标

    for i, line in enumerate(lines):
        draw.text((left_margin, y), line, font=waves_font_24, fill=title_color)
        if i == 0:
            y += 60
        else:
            y += 45

    return img
