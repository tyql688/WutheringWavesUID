import asyncio
import copy
import json as j
import random
from typing import Literal, Optional, Union, Dict, Any, List

from PIL import Image, ImageDraw
from aiohttp import FormData, ClientSession, TCPConnector, ContentTypeError

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.utils.boardcast.models import BoardCastMsg, BoardCastMsgDict
from gsuid_core.utils.image.convert import convert_img
from ..utils.api.api import MAIN_URL
from ..utils.api.model import DailyData
from ..utils.database.models import WavesUser, WavesBind
from ..utils.error_reply import WAVES_CODE_999, ERROR_CODE, WAVES_CODE_102, WAVES_CODE_101
from ..utils.fonts.waves_fonts import waves_font_30, waves_font_20, waves_font_16
from ..utils.util import generate_random_string
from ..utils.waves_api import waves_api

GET_GOLD_URL = f'{MAIN_URL}/encourage/gold/getTotalGold'
GET_TASK_URL = f'{MAIN_URL}/encourage/level/getTaskProcess'
FORUM_LIST_URL = f'{MAIN_URL}/forum/list'
LIKE_URL = f'{MAIN_URL}/forum/like'
SIGN_IN_URL = f'{MAIN_URL}/user/signIn'
POST_DETAIL_URL = f'{MAIN_URL}/forum/getPostDetail'
SHARE_URL = f'{MAIN_URL}/encourage/level/shareTask'


async def get_headers_h5():
    devCode = generate_random_string()
    header = {
        "source": "h5",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "devCode": devCode
    }
    return header


async def get_headers_ios():
    devCode = generate_random_string()
    header = {
        "source": "ios",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "KuroGameBox/55 CFNetwork/1399 Darwin/22.1.0",
        "devCode": devCode
    }
    return header


async def get_headers(ck: str = None, platform: str = None):
    if ck and not platform:
        try:
            waves_user = await WavesUser.select_data_by_cookie(cookie=ck)
            platform = waves_user.platform
        except Exception as _:
            pass

    if platform == 'h5' or not platform:
        return await get_headers_h5()
    elif platform == 'ios':
        return await get_headers_ios()


class KuroBBS:
    ssl_verify = True

    async def get_task(self, token: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(await get_headers())
        header.update({"token": token})
        data = {"gameId": "0"}
        return await self._waves_request(GET_TASK_URL, "POST", header, data=data)

    async def get_form_list(self, token: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(await get_headers())
        header.update({"token": token, "version": "2.25"})
        data = {
            "pageIndex": "1",
            "pageSize": "20",
            "timeType": "0",
            "searchType": "1",
            "forumId": "9",
            "gameId": "3"
        }
        return await self._waves_request(FORUM_LIST_URL, "POST", header, data=data)

    async def get_gold(self, token: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(await get_headers())
        header.update({"token": token})
        return await self._waves_request(GET_GOLD_URL, "POST", header)

    async def do_like(self, token: str, postId, toUserId) -> (bool, Union[Dict, str]):
        """点赞"""
        header = copy.deepcopy(await get_headers())
        header.update({"token": token})
        data = {
            'gameId': "3",  # 鸣潮
            'likeType': "1",  # 1.点赞帖子 2.评论
            'operateType': "1",  # 1.点赞 2.取消
            'postId': postId,
            'toUserId': toUserId
        }
        return await self._waves_request(LIKE_URL, "POST", header, data=data)

    async def do_sign_in(self, token: str) -> (bool, Union[Dict, str]):
        """签到"""
        header = copy.deepcopy(await get_headers())
        header.update({"token": token})
        data = {"gameId": "3"}
        return await self._waves_request(SIGN_IN_URL, "POST", header, data=data)

    async def do_post_detail(self, token: str, postId) -> (bool, Union[Dict, str]):
        """浏览"""
        header = copy.deepcopy(await get_headers())
        header.update({"token": token})
        data = {'gameId': "3", "postId": postId}
        return await self._waves_request(POST_DETAIL_URL, "POST", header, data=data)

    async def do_share(self, token: str) -> (bool, Union[Dict, str]):
        """分享"""
        header = copy.deepcopy(await get_headers())
        header.update({"token": token})
        data = {'gameId': "3"}
        return await self._waves_request(SHARE_URL, "POST", header, data=data)

    async def _waves_request(
        self,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        header=None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[FormData, Dict[str, Any]]] = None,
    ) -> Union[Dict, int]:

        if header is None:
            header = await get_headers()

        async with ClientSession(
            connector=TCPConnector(verify_ssl=self.ssl_verify)
        ) as client:
            async with client.request(
                method,
                url=url,
                headers=header,
                params=params,
                json=json,
                data=data,
                timeout=300,
            ) as resp:
                try:
                    raw_data = await resp.json()
                except ContentTypeError:
                    _raw_data = await resp.text()
                    raw_data = {"code": WAVES_CODE_999, "data": _raw_data}
                if isinstance(raw_data, dict) and 'data' in raw_data and isinstance(raw_data['data'], str):
                    try:
                        des_data = j.loads(raw_data['data'])
                        raw_data['data'] = des_data
                    except:
                        pass
                logger.debug(f'url:[{url}] raw_data:{raw_data}')
                return raw_data


bbs_api = KuroBBS()


async def do_sign_in(taskData, uid, token, form_result):
    key = '签到'
    form_result[uid][key] = -1
    if taskData['completeTimes'] == taskData['needActionTimes']:
        form_result[uid][key] = taskData['needActionTimes'] - taskData['completeTimes']
        return

    # 用户签到
    sign_in_res = await bbs_api.do_sign_in(token)
    if isinstance(sign_in_res, dict):
        if sign_in_res.get('code') == 200 and sign_in_res.get('data'):
            # 签到成功
            form_result[uid][key] = taskData['needActionTimes']
            return
    logger.warning(f'[鸣潮][社区签到]签到失败 uid: {uid}')


async def do_detail(taskData, uid, token, form_result, post_list):
    key = '浏览'
    form_result[uid][key] = -1
    if taskData['completeTimes'] == taskData['needActionTimes']:
        form_result[uid][key] = taskData['needActionTimes'] - taskData['completeTimes']
        return
    # 浏览帖子
    detail_succ = 0
    for i, post in enumerate(post_list):
        post_detail_res = await bbs_api.do_post_detail(token, post['postId'])
        if isinstance(post_detail_res, dict):
            if post_detail_res.get('code') == 200:
                detail_succ += 1
                # 浏览成功
                form_result[uid]['浏览'] = detail_succ
        if detail_succ >= taskData['needActionTimes'] - taskData['completeTimes']:
            return

    logger.warning(f'[鸣潮][社区签到]浏览失败 uid: {uid}')


async def do_like(taskData, uid, token, form_result, post_list):
    key = '点赞'
    form_result[uid][key] = -1
    if taskData['completeTimes'] == taskData['needActionTimes']:
        form_result[uid][key] = taskData['needActionTimes'] - taskData['completeTimes']
        return

    # 用户点赞5次
    like_succ = 0
    for i, post in enumerate(post_list):
        like_res = await bbs_api.do_like(token, post['postId'], post['userId'])
        if isinstance(like_res, dict):
            if like_res.get('code') == 200:
                like_succ += 1
                # 点赞成功
                form_result[uid][key] = like_succ
        if like_succ >= taskData['needActionTimes'] - taskData['completeTimes']:
            return

    logger.warning(f'[鸣潮][社区签到]点赞失败 uid: {uid}')


async def do_share(taskData, uid, token, form_result):
    key = '分享'
    form_result[uid][key] = -1
    if taskData['completeTimes'] == taskData['needActionTimes']:
        form_result[uid][key] = taskData['needActionTimes'] - taskData['completeTimes']
        return

    # 分享
    share_res = await bbs_api.do_share(token)
    if isinstance(share_res, dict):
        if share_res.get('code') == 200:
            # 分享成功
            form_result[uid][key] = taskData['needActionTimes']
            return

    logger.exception(f'[鸣潮][社区签到]分享失败 uid: {uid}')


async def do_task(bot: Bot, ev: Event):
    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return ERROR_CODE[WAVES_CODE_102]
    # 进行校验UID是否绑定CK
    valid_ck_list = []
    for uid in uid_list:
        ck = await waves_api.get_self_waves_ck(uid)
        if not ck:
            continue
        succ, _ = await waves_api.refresh_data(uid, ck)
        if not succ:
            continue

        valid_ck_list.append((uid, ck))

    if len(valid_ck_list) == 0:
        return ERROR_CODE[WAVES_CODE_102]

    form_result = {}
    for uid, token in valid_ck_list:
        res = await do_single_task(uid, token)
        if res:
            form_result[uid] = res[uid]

    card_img = await draw_task(form_result)
    card_img = await convert_img(card_img)
    return card_img


async def do_single_task(uid, token):
    # 任务列表
    task_res = await bbs_api.get_task(token)
    if not isinstance(task_res, dict):
        return
    if task_res.get('code') != 200 or not task_res.get('data'):
        return

        # check 1
    need_post_list_flag = False
    for i in task_res['data']['dailyTask']:
        if i['completeTimes'] == i['needActionTimes']:
            continue
        if '签到' not in i['remark'] or '分享' not in i['remark']:
            need_post_list_flag = True

    post_list = []
    if need_post_list_flag:
        # 获取帖子
        form_list_res = await bbs_api.get_form_list(token)
        if isinstance(form_list_res, dict):
            if form_list_res.get('code') == 200 and form_list_res.get('data'):
                # 获取到帖子列表
                post_list = form_list_res['data']['postList']
        if not post_list:
            logger.exception(f'[鸣潮][社区签到]获取帖子列表失败 uid: {uid} res: {form_list_res}')
            # 未获取帖子列表
            return

    form_result = {
        uid: {
            '签到': '', '浏览': '', '点赞': '', '分享': '', '库洛币': ''
        }}
    # 获取到任务列表
    for i in task_res['data']['dailyTask']:
        if '签到' in i['remark']:
            await do_sign_in(i, uid, token, form_result)
        elif '浏览' in i['remark']:
            await do_detail(i, uid, token, form_result, post_list)
        elif '点赞' in i['remark']:
            await do_like(i, uid, token, form_result, post_list)
        elif '分享' in i['remark']:
            await do_share(i, uid, token, form_result)

    gold_res = await bbs_api.get_gold(token)
    if isinstance(gold_res, dict):
        if gold_res.get('code') == 200:
            form_result[uid]['库洛币'] = gold_res["data"]["goldNum"]

    return form_result


async def draw_task(user_data):
    # 设置基本参数
    base_width = 900
    min_height = 100
    cell_height = 60
    header_height = 100
    footer_height = 100
    row_margin = 10

    title_font = waves_font_30
    header_font = waves_font_20
    content_font = waves_font_16

    # 计算所需的图片高度
    num_rows = len(user_data)
    table_height = (cell_height + row_margin) * num_rows
    height = max(min_height, header_height + table_height + footer_height)

    # 创建图片对象
    image = Image.new('RGB', (base_width, height), (240, 248, 255))
    draw = ImageDraw.Draw(image)

    # 创建渐变背景
    for y in range(height):
        r = int(240 + (255 - 240) * (y / height))
        g = int(248 + (255 - 248) * (y / height))
        b = 255
        for x in range(base_width):
            draw.point((x, y), fill=(r, g, b))

    # 绘制标题
    title = "库街区签到任务"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    draw.text(((base_width - title_width) / 2, 30), title, font=title_font, fill=(0, 0, 128))

    # 定义表格参数
    table_top = header_height
    col_widths = [180, 120, 120, 120, 120, 120]
    headers = ['特征码', '签到', '浏览', '点赞', '分享', '库洛币']

    # 绘制表头
    x = 60
    for i, header in enumerate(headers):
        draw.rounded_rectangle([x, table_top, x + col_widths[i], table_top + cell_height],
                               radius=10, fill=(230, 230, 250), outline=(0, 0, 128))
        text_bbox = draw.textbbox((0, 0), header, font=header_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((x + (col_widths[i] - text_width) / 2, table_top + (cell_height - text_height) / 2),
                  header, font=header_font, fill=(0, 0, 128))
        x += col_widths[i]

    # 绘制数据行
    for row, (user_id, data) in enumerate(user_data.items()):
        y = table_top + (cell_height + row_margin) * (row + 1)
        x = 60
        for col, key in enumerate(headers):
            draw.rounded_rectangle([x, y, x + col_widths[col], y + cell_height],
                                   radius=10, fill=(255, 255, 255), outline=(200, 200, 200))
            if col == 0:
                text = user_id
            else:
                text = str(data.get(key, ''))

            if key in ['签到', '浏览', '点赞', '分享']:
                if data[key] == 0:
                    text = '已完成'
                    fill_color = (255, 255, 224)
                elif data[key] == -1:
                    text = '失败'
                    fill_color = (255, 182, 193)
                else:
                    fill_color = (144, 238, 144)
                draw.rounded_rectangle([x + 2, y + 2, x + col_widths[col] - 2, y + cell_height - 2],
                                       radius=8, fill=fill_color)

            text_bbox = draw.textbbox((0, 0), text, font=content_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.text((x + (col_widths[col] - text_width) / 2, y + (cell_height - text_height) / 2),
                      text, font=content_font, fill=(0, 0, 0))
            x += col_widths[col]

    return image


async def single_task(
    bot_id: str,
    uid: str,
    gid: str,
    qid: str,
    ck: str,
    private_msgs: Dict,
    group_msgs: Dict,
):
    im = await do_single_task(uid, ck)
    if not im:
        return
    msg = []
    msg.append(f'特征码: {uid}')
    for i, r in im[str(uid)].items():
        if r == 0:
            r = '已完成'
        elif r == -1:
            r = '失败'
        else:
            r = f'{r}' if i == '库洛币' else f'成功{r}次'
        msg.append(f'{i}: {r}')

    im = '\n'.join(msg)
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
            group_msgs[gid]['success'] += 1


async def auto_bbs_task():
    tasks = []
    private_msgs = {}
    group_msgs = {}
    _user_list: List[WavesUser] = await WavesUser.get_waves_all_user()

    user_list: List[WavesUser] = []
    for user in _user_list:
        _uid = user.user_id
        _switch = user.bbs_sign_switch
        if _switch != 'off' and not user.status and _uid:
            user_list.append(user)

    for user in user_list:
        succ, _ = await waves_api.refresh_data(user.uid, user.cookie)
        if not succ:
            continue
        tasks.append(
            single_task(
                user.bot_id,
                user.uid,
                user.bbs_sign_switch,
                user.user_id,
                user.cookie,
                private_msgs,
                group_msgs,
            ))
        if len(tasks) >= 1:
            await asyncio.gather(*tasks)
            delay = 5 + random.randint(1, 5)
            logger.info(
                f'[鸣潮] [社区签到] 已签到{len(tasks)}个用户, 等待{delay}秒进行下一次签到'
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
        title = f'✅[鸣潮]今日社区签到任务已完成！\n📝本群共签到成功{success}人，共签到失败{faild}人。'
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


async def do_sign_task(bot: Bot, ev: Event):
    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return ERROR_CODE[WAVES_CODE_102]
    # 进行校验UID是否绑定CK
    valid_ck_list = []

    expire_uid = []
    for uid in uid_list:
        ck = await waves_api.get_self_waves_ck(uid)
        if not ck:
            continue
        succ, _ = await waves_api.refresh_data(uid, ck)
        if not succ:
            expire_uid.append(uid)
            continue

        valid_ck_list.append((uid, ck))

    form_result = {}
    for uid, token in valid_ck_list:
        res = await do_single_task(uid, token)
        if res:
            form_result[uid] = res[uid]

        res = await sign_in2(uid, token)
        if res:
            if not isinstance(form_result[uid], dict):
                form_result[uid] = {}
            form_result[uid]['游戏签到'] = res

    msg_list = []
    for uid, temp in form_result.items():
        msg_list.append(f'账号 {uid} 签到结果')
        msg_list.append('')
        if '游戏签到' in temp:
            msg_list.append(f'------: 游戏签到 :------')
            msg_list.append(f'[游戏签到] {temp["游戏签到"]}')
            temp.pop('游戏签到')
            msg_list.append('')

        if len(temp) == 0:
            continue
        msg_list.append(f'------: 社区签到 :------')
        for title, value in temp.items():
            if value == 0:
                value = '今日已完成！'
            msg_list.append(f'[{title}] {value}')

        msg_list.append('====================')

    for uid in expire_uid:
        msg_list.append(f'失效特征码: {uid}')

    return '\n'.join(msg_list)


async def sign_in2(uid: str, ck: str) -> str:
    succ, daily_info = await waves_api.get_daily_info(ck)
    if not succ:
        # 检查ck
        return f'{ERROR_CODE[WAVES_CODE_101]}'

    daily_info = DailyData(**daily_info)
    if daily_info.hasSignIn:
        # 已经签到
        logger.debug(f'UID{uid} 该用户今日已签到,跳过...')
        return f'今日已签到！请勿重复签到！'

    sign_in_res = await waves_api.sign_in(daily_info.roleId, ck)
    if isinstance(sign_in_res, dict):
        if sign_in_res.get('code') == 200 and sign_in_res.get('data'):
            # 签到成功
            return f'签到成功！'
        elif sign_in_res.get('code') == 1511:
            # 已经签到
            logger.debug(f'UID{uid} 该用户今日已签到,跳过...')
            return f'今日已签到！请勿重复签到！'
    # 签到失败
    return f'签到失败！'
