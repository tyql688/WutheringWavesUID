import copy
import json as j
from typing import Literal, Optional, Union, Dict, Any

from aiohttp import FormData, ClientSession, TCPConnector, ContentTypeError

from gsuid_core.logger import logger
from ..utils.api.api import MAIN_URL
from ..utils.database.models import WavesUser
from ..utils.error_reply import WAVES_CODE_999
from ..utils.util import generate_random_string

GET_GOLD_URL = f"{MAIN_URL}/encourage/gold/getTotalGold"
GET_TASK_URL = f"{MAIN_URL}/encourage/level/getTaskProcess"
FORUM_LIST_URL = f"{MAIN_URL}/forum/list"
LIKE_URL = f"{MAIN_URL}/forum/like"
SIGN_IN_URL = f"{MAIN_URL}/user/signIn"
POST_DETAIL_URL = f"{MAIN_URL}/forum/getPostDetail"
SHARE_URL = f"{MAIN_URL}/encourage/level/shareTask"


async def get_headers_h5():
    devCode = generate_random_string()
    header = {
        "source": "h5",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "devCode": devCode,
    }
    return header


async def get_headers_ios():
    devCode = generate_random_string()
    header = {
        "source": "ios",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "KuroGameBox/1 CFNetwork/1399 Darwin/22.1.0",
        "devCode": devCode,
    }
    return header


async def get_headers(ck: str = None, platform: str = None):
    if ck and not platform:
        try:
            waves_user = await WavesUser.select_data_by_cookie(cookie=ck)
            platform = waves_user.platform
        except Exception as _:
            pass
    if platform == "h5" or not platform:
        return await get_headers_h5()
    elif platform == "ios":
        return await get_headers_ios()


class KuroBBS:
    ssl_verify = True

    async def get_task(self, token: str) -> (bool, Union[Dict, str]):
        try:
            header = copy.deepcopy(await get_headers(token))
            header.update({"token": token})
            data = {"gameId": "0"}
            return await self._waves_request(GET_TASK_URL, "POST", header, data=data)
        except Exception as e:
            logger.exception(f"get_task token {token}", e)

    async def get_form_list(self, token: str) -> (bool, Union[Dict, str]):
        try:
            header = copy.deepcopy(await get_headers(token))
            header.update({"token": token, "version": "2.25"})
            data = {
                "pageIndex": "1",
                "pageSize": "20",
                "timeType": "0",
                "searchType": "1",
                "forumId": "9",
                "gameId": "3",
            }
            return await self._waves_request(FORUM_LIST_URL, "POST", header, data=data)
        except Exception as e:
            logger.exception(f"get_form_list token {token}", e)

    async def get_gold(self, token: str) -> (bool, Union[Dict, str]):
        try:
            header = copy.deepcopy(await get_headers(token))
            header.update({"token": token})
            return await self._waves_request(GET_GOLD_URL, "POST", header)
        except Exception as e:
            logger.exception(f"get_gold token {token}", e)

    async def do_like(self, token: str, postId, toUserId) -> (bool, Union[Dict, str]):
        """点赞"""
        try:
            header = copy.deepcopy(await get_headers(token))
            header.update({"token": token})
            data = {
                "gameId": "3",  # 鸣潮
                "likeType": "1",  # 1.点赞帖子 2.评论
                "operateType": "1",  # 1.点赞 2.取消
                "postId": postId,
                "toUserId": toUserId,
            }
            return await self._waves_request(LIKE_URL, "POST", header, data=data)
        except Exception as e:
            logger.exception(f"do_like token {token}", e)

    async def do_sign_in(self, token: str) -> (bool, Union[Dict, str]):
        """签到"""
        try:
            header = copy.deepcopy(await get_headers(token))
            header.update({"token": token})
            data = {"gameId": "2"}
            return await self._waves_request(SIGN_IN_URL, "POST", header, data=data)
        except Exception as e:
            logger.exception(f"do_sign_in token {token}", e)

    async def do_post_detail(self, token: str, postId) -> (bool, Union[Dict, str]):
        """浏览"""
        try:
            header = copy.deepcopy(await get_headers(token))
            header.update({"token": token})
            data = {"gameId": "3", "postId": postId}
            return await self._waves_request(POST_DETAIL_URL, "POST", header, data=data)
        except Exception as e:
            logger.exception(f"do_post_detail token {token}", e)

    async def do_share(self, token: str) -> (bool, Union[Dict, str]):
        """分享"""
        try:
            header = copy.deepcopy(await get_headers(token))
            header.update({"token": token})
            data = {"gameId": "3"}
            return await self._waves_request(SHARE_URL, "POST", header, data=data)
        except Exception as e:
            logger.exception(f"do_share token {token}", e)

    async def check_bbs_completed(self, token: str) -> bool:
        task_res = await self.get_task(token)
        if not isinstance(task_res, dict):
            return False
        if task_res.get("code") != 200 or not task_res.get("data"):
            return False
        for i in task_res["data"]["dailyTask"]:
            if i["completeTimes"] != i["needActionTimes"]:
                return False
        return True

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
                if (
                    isinstance(raw_data, dict)
                    and "data" in raw_data
                    and isinstance(raw_data["data"], str)
                ):
                    try:
                        des_data = j.loads(raw_data["data"])
                        raw_data["data"] = des_data
                    except:
                        pass
                logger.debug(f"url:[{url}] raw_data:{raw_data}")
                return raw_data


bbs_api = KuroBBS()
