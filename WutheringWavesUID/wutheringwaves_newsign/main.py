import asyncio
import random
from typing import Dict, Union

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.segment import MessageSegment

from ..utils.api.model import DailyData
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_101
from ..utils.fonts.waves_fonts import waves_font_24
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import WutheringWavesConfig
from .bbs_api import bbs_api


async def get_sign_interval(is_bbs: bool = False):
    next_group_sign_time = WutheringWavesConfig.get_config(
        "SigninConcurrentNumInterval2"
    ).data
    ratio = random.uniform(1, 2) if is_bbs else 1
    if not next_group_sign_time:
        return random.uniform(2, 3) * ratio
    return (
        random.uniform(float(next_group_sign_time[0]), float(next_group_sign_time[1]))
        * ratio
    )


async def do_sign_in(taskData, uid, token):
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        return True

    # 用户签到
    sign_in_res = await bbs_api.do_sign_in(token)
    if isinstance(sign_in_res, dict):
        if sign_in_res.get("code") == 200 and sign_in_res.get("data"):
            # 签到成功
            return True
    logger.warning(f"[鸣潮][社区签到]签到失败 uid: {uid} sign_in_res: {sign_in_res}")
    return False


async def do_detail(taskData, uid, token, post_list):
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        return True
    # 浏览帖子
    detail_succ = 0
    for i, post in enumerate(post_list):
        post_detail_res = await bbs_api.do_post_detail(token, post["postId"])
        if isinstance(post_detail_res, dict):
            if post_detail_res.get("code") == 200:
                detail_succ += 1
                # 浏览成功
        if detail_succ >= taskData["needActionTimes"] - taskData["completeTimes"]:
            return True

    logger.warning(f"[鸣潮][社区签到]浏览失败 uid: {uid}")
    return False


async def do_like(taskData, uid, token, post_list):
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        return True

    # 用户点赞5次
    like_succ = 0
    for i, post in enumerate(post_list):
        like_res = await bbs_api.do_like(token, post["postId"], post["userId"])
        if isinstance(like_res, dict):
            if like_res.get("code") == 200:
                like_succ += 1
                # 点赞成功
        if like_succ >= taskData["needActionTimes"] - taskData["completeTimes"]:
            return True

    logger.warning(f"[鸣潮][社区签到]点赞失败 uid: {uid}")
    return False


async def do_share(taskData, uid, token):
    if taskData["completeTimes"] == taskData["needActionTimes"]:
        return True

    # 分享
    share_res = await bbs_api.do_share(token)
    if isinstance(share_res, dict):
        if share_res.get("code") == 200:
            # 分享成功
            return True

    logger.exception(f"[鸣潮][社区签到]分享失败 uid: {uid}")
    return False


async def do_single_task(uid, token) -> Union[bool, Dict[str, bool]]:
    # 任务列表
    task_res = await bbs_api.get_task(token)
    if not isinstance(task_res, dict):
        return False
    if task_res.get("code") != 200 or not task_res.get("data"):
        return False

    for i in task_res["data"]["dailyTask"]:
        if i["completeTimes"] != i["needActionTimes"]:
            break
    else:
        return True

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
            return False

    form_result = {
        uid: {
            "用户签到": False,
            "浏览帖子": False,
            "点赞帖子": False,
            "分享帖子": False,
        }
    }

    # 获取到任务列表
    for i in task_res["data"]["dailyTask"]:
        if "签到" in i["remark"]:
            form_result[uid]["用户签到"] = await do_sign_in(i, uid, token)
        elif "浏览" in i["remark"]:
            form_result[uid]["浏览帖子"] = await do_detail(i, uid, token, post_list)
        elif "点赞" in i["remark"]:
            form_result[uid]["点赞帖子"] = await do_like(i, uid, token, post_list)
        elif "分享" in i["remark"]:
            form_result[uid]["分享帖子"] = await do_share(i, uid, token)

        await asyncio.sleep(random.uniform(0, 1))

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
    if isinstance(im, dict):
        msg = []
        msg.append(f"特征码: {uid}")
        for i, r in im[str(uid)].items():
            if r:
                msg.append(f"{i}: 成功")
            else:
                msg.append(f"{i}: 失败")

        im = "\n".join(msg)
    elif isinstance(im, bool):
        if im:
            im = "社区签到成功"
        else:
            im = "社区签到失败"
    else:
        return

    logger.debug(f"[鸣潮][社区签到]签到结果 uid: {uid} res: {im}")

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


async def sign_in(uid: str, ck: str) -> str:
    succ, daily_info = await waves_api.get_daily_info(ck)
    if not succ:
        # 检查ck
        return f"签到失败！\n{ERROR_CODE[WAVES_CODE_101]}"

    daily_info = DailyData.model_validate(daily_info)
    if daily_info.hasSignIn:
        # 已经签到
        logger.debug(f"UID{uid} 该用户今日已签到,跳过...")
        return "今日已签到！请勿重复签到！"

    sign_in_res = await waves_api.sign_in(daily_info.roleId, ck)
    if isinstance(sign_in_res, dict):
        if sign_in_res.get("code") == 200 and sign_in_res.get("data"):
            # 签到成功
            return "签到成功！"
        elif sign_in_res.get("code") == 1511:
            # 已经签到
            logger.debug(f"UID{uid} 该用户今日已签到,跳过...")
            return "今日已签到！请勿重复签到！"
    # 签到失败
    return "签到失败！"


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
