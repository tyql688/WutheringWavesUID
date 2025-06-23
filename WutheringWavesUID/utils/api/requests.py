import asyncio
import inspect
import json
import random
from typing import Any, Dict, List, Literal, Optional, Union

import aiohttp
from aiohttp import ClientTimeout, ContentTypeError

from gsuid_core.logger import logger

from ...wutheringwaves_config import WutheringWavesConfig
from ..database.models import WavesUser
from ..error_reply import (
    WAVES_CODE_107,
    WAVES_CODE_990,
    WAVES_CODE_998,
    WAVES_CODE_999,
)
from ..hint import error_reply
from ..util import (
    generate_random_ipv6_manual,
    generate_random_string,
    get_public_ip,
    login_platform,
    send_master_info,
    timed_async_cache,
)
from .api import (
    ANN_CONTENT_URL,
    ANN_LIST_URL,
    BASE_DATA_URL,
    BATCH_ROLE_COST,
    CALABASH_DATA_URL,
    CALCULATOR_REFRESH_DATA_URL,
    CHALLENGE_DATA_URL,
    EXPLORE_DATA_URL,
    GACHA_LOG_URL,
    GACHA_NET_LOG_URL,
    GAME_ID,
    LOGIN_H5_URL,
    LOGIN_LOG_URL,
    LOGIN_URL,
    MONTH_LIST_URL,
    MR_REFRESH_URL,
    NET_SERVER_ID_MAP,
    ONLINE_LIST_PHANTOM,
    ONLINE_LIST_ROLE,
    ONLINE_LIST_WEAPON,
    PERIOD_LIST_URL,
    QUERY_OWNED_ROLE,
    REFRESH_URL,
    REQUEST_TOKEN,
    ROLE_CULTIVATE_STATUS,
    ROLE_DATA_URL,
    ROLE_DETAIL_URL,
    ROLE_LIST_URL,
    SERVER_ID,
    SERVER_ID_NET,
    SLASH_DETAIL_URL,
    SLASH_INDEX_URL,
    TOWER_DETAIL_URL,
    TOWER_INDEX_URL,
    VERSION_LIST_URL,
    WEEK_LIST_URL,
    WIKI_DETAIL_URL,
    WIKI_ENTRY_DETAIL_URL,
    WIKI_HOME_URL,
    WIKI_TREE_URL,
    get_local_proxy_url,
    get_need_proxy_func,
)
from .captcha import get_solver
from .captcha.base import CaptchaResult
from .captcha.errors import CaptchaError


async def _check_response(
    res: Union[Dict, int],
    token: Optional[str] = None,
    roleId=None,
) -> tuple[bool, Union[Dict, str]]:
    if isinstance(res, dict):
        res_code = res.get("code")
        res_msg = res.get("msg")
        res_data = res.get("data")
        if res_code == 200 and res_data:
            return True, res_data

        if res_code == 10902 and res_data:
            return True, res_data

        if res_msg and (res_msg == "请求成功" or res_msg == "系统繁忙，请稍后再试"):
            msg = f"\n鸣潮账号id: 【{roleId}】未绑定库街区!!!\n1.是否注册过库街区\n2.库街区能否查询当前鸣潮账号数据\n"
            return False, error_reply(None, msg)

        logger.warning(f"[wwuid] code: {res_code} msg: {res_msg} data: {res_data}")

        if res_msg and ("重新登录" in res_msg or "登录已过期" in res_msg):
            if token and roleId:
                await WavesUser.mark_cookie_invalid(roleId, token, "无效")
            elif token:
                await WavesUser.mark_invalid(token, "无效")
            return False, res_msg

        if isinstance(res_data, str) and (
            "RABC" in res_data or "access denied" in res_data
        ):
            await send_master_info(res_data)
            return False, error_reply(WAVES_CODE_998)

        if res_msg and "访问被阻断" in res_msg:
            await send_master_info(res_msg)
            return False, error_reply(WAVES_CODE_998)

        if res_msg:
            await send_master_info(res_msg)
            code = res_code if res_code else WAVES_CODE_999
            return False, error_reply(code, res_msg)
    return False, error_reply(WAVES_CODE_999)


KURO_VERSION = "2.5.0"
KURO_VERSION_CODE = "2500"


async def get_common_header(platform: str = "ios"):
    devCode = generate_random_string()
    header = {
        "source": platform,
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "devCode": devCode,
        "X-Forwarded-For": generate_random_ipv6_manual(),
        "version": KURO_VERSION,
    }
    return header


async def get_headers_h5():
    devCode = generate_random_string()
    header = {
        "source": "h5",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "devCode": devCode,
        "X-Forwarded-For": generate_random_ipv6_manual(),
        "version": KURO_VERSION,
    }
    return header


async def get_headers_ios():
    ip = await get_public_ip()
    header = {
        "source": "ios",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  KuroGameBox/2.5.0",
        "devCode": f"{ip}, Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  KuroGameBox/2.5.0",
        "X-Forwarded-For": generate_random_ipv6_manual(),
    }
    return header


async def get_headers(
    ck: Optional[str] = None,
    platform: Optional[str] = None,
    queryRoleId: Optional[str] = None,
) -> Dict:
    if not ck and not platform:
        return await get_headers_h5()

    bat = ""
    did = ""
    tokenRoleId = ""
    platform = "ios"
    if ck:
        # 获取当前role信息
        if queryRoleId:
            waves_user = await WavesUser.select_data_by_cookie_and_uid(
                cookie=ck, uid=queryRoleId
            )
            if waves_user:
                platform = waves_user.platform
                bat = waves_user.bat
                did = waves_user.did
                tokenRoleId = waves_user.uid

                logger.debug(
                    f"[get_headers.self.{inspect.stack()[1].function}] [queryRoleId:{queryRoleId} tokenRoleId:{tokenRoleId}] 获取成功: did: {did} bat: {bat}"
                )

        # 2次校验
        if not tokenRoleId:
            waves_user = await WavesUser.select_data_by_cookie(cookie=ck)
            if waves_user:
                platform = waves_user.platform
                bat = waves_user.bat
                did = waves_user.did
                tokenRoleId = waves_user.uid

                logger.debug(
                    f"[get_headers.other.{inspect.stack()[1].function}.2] [queryRoleId:{queryRoleId} tokenRoleId:{tokenRoleId}] 获取成功: did: {did} bat: {bat}"
                )

    if platform == "ios":
        header = await get_headers_ios()
    else:
        header = await get_common_header(platform or "ios")
    if bat:
        header.update({"b-at": bat})
    if did:
        header.update({"did": did})
    if tokenRoleId:
        header.update({"roleId": tokenRoleId})
    return header


class WavesApi:
    ssl_verify = True
    ann_map = {}
    ann_list_data = []
    event_type = {"2": "资讯", "3": "公告", "1": "活动"}

    entry_detail_map = {}
    bat_map = {}

    _sessions: Dict[str, aiohttp.ClientSession] = {}
    _session_lock = asyncio.Lock()

    def __init__(self):
        self.captcha_solver = get_solver()
        if self.captcha_solver:
            logger.success(f"使用过码器: {self.captcha_solver.get_name()}")

    async def get_session(self, proxy: Optional[str] = None) -> aiohttp.ClientSession:
        key = f"{proxy or 'no_proxy'}"

        if key in self._sessions and not self._sessions[key].closed:
            return self._sessions[key]

        async with self._session_lock:
            if key in self._sessions and not self._sessions[key].closed:
                return self._sessions[key]

            session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self.ssl_verify),
            )

            self._sessions[key] = session
            return session

    def is_net(self, roleId):
        _temp = int(roleId)
        return _temp >= 200000000

    def get_server_id(self, roleId, serverId: Optional[str] = None):
        if serverId:
            return serverId
        if self.is_net(roleId):
            return NET_SERVER_ID_MAP.get(int(roleId) // 100000000, SERVER_ID_NET)
        return SERVER_ID

    async def get_ck_result(self, uid, user_id, bot_id) -> tuple[bool, Optional[str]]:
        ck = await self.get_self_waves_ck(uid, user_id, bot_id)
        if ck:
            return True, ck
        ck = await self.get_waves_random_cookie(uid, user_id)
        return False, ck

    async def get_self_waves_ck(
        self,
        uid: str,
        user_id: str,
        bot_id: str,
    ) -> Optional[str]:
        waves_user = await WavesUser.select_waves_user(uid, user_id, bot_id)
        if not waves_user or not waves_user.cookie:
            return ""

        if waves_user.status == "无效":
            return ""

        succ, data = await self.login_log(uid, waves_user.cookie)
        if not succ:
            if "重新登录" in data or "登录已过期" in data:
                await WavesUser.mark_cookie_invalid(uid, waves_user.cookie, "无效")
            return ""

        succ, data = await self.refresh_data(uid, waves_user.cookie)
        if succ:
            return waves_user.cookie

        if "重新登录" in data or "登录已过期" in data:
            await WavesUser.mark_cookie_invalid(uid, waves_user.cookie, "无效")
            return ""

        if isinstance(data, str):
            logger.warning(f"[{uid}] 获取ck失败: {data}")

        # 返回空串 表示绑定已失效
        return ""

    async def get_waves_random_cookie(self, uid: str, user_id: str) -> Optional[str]:
        if WutheringWavesConfig.get_config("WavesOnlySelfCk").data:
            return None

        # 公共ck 随机一个
        user_list = await WavesUser.get_waves_all_user()
        random.shuffle(user_list)
        ck_list = []
        times = 1
        for user in user_list:
            if not await WavesUser.cookie_validate(user.uid):
                continue

            succ, data = await self.login_log(user.uid, user.cookie)
            if not succ:
                if "重新登录" in data or "登录已过期" in data:
                    await WavesUser.mark_cookie_invalid(user.uid, user.cookie, "无效")
                continue

            succ, data = await self.refresh_data(user.uid, user.cookie)
            if not succ:
                if "重新登录" in data or "登录已过期" in data:
                    await WavesUser.mark_cookie_invalid(user.uid, user.cookie, "无效")

                if "封禁" in data:
                    break

                if times <= 0:
                    break

                times -= 1
                continue

            ck_list.append(user.cookie)
            break

        if len(ck_list) > 0:
            return random.choices(ck_list, k=1)[0]

    async def get_kuro_role_list(
        self, token: str, did: str
    ) -> tuple[bool, str, Union[List, str, int]]:
        platform = login_platform()
        header = await get_common_header(platform=platform)
        header.update(
            {
                "token": token,
                "devCode": did,
            }
        )

        data = {"gameId": GAME_ID}

        err_msg = error_reply(WAVES_CODE_999)
        raw_data = await self._waves_request(ROLE_LIST_URL, "POST", header, data=data)
        if isinstance(raw_data, dict):
            if raw_data.get("code") == 200 and raw_data.get("data"):
                return True, platform, raw_data["data"]

            logger.warning(f"get_kuro_role_list -> msg: {raw_data}")
            if raw_data.get("msg"):
                err_msg = raw_data["msg"]
                return False, "", err_msg
        return False, "", err_msg

    async def get_daily_info(
        self, roleId: str, token: str, gameId: Union[str, int] = GAME_ID
    ) -> tuple[bool, Union[Dict, str]]:
        """每日"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "type": "1",
            "sizeType": "2",
            "gameId": gameId,
            "serverId": self.get_server_id(roleId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(
            MR_REFRESH_URL,
            "POST",
            header,
            data=data,
        )
        return await _check_response(raw_data, token)

    async def refresh_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> tuple[bool, Union[Dict, str]]:
        """刷新数据"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(REFRESH_URL, "POST", header, data=data)
        return await _check_response(raw_data, token, roleId)

    async def login_log(self, roleId: str, token: str):
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update(
            {
                "token": token,
                "devCode": header.get("did", ""),
                "version": KURO_VERSION,
            }
        )
        header.pop("did", None)
        header.pop("b-at", None)

        data = {}
        raw_data = await self._waves_request(LOGIN_LOG_URL, "POST", header, data=data)
        return await _check_response(raw_data, token, roleId)

    async def get_base_info(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> tuple[bool, Union[Dict, str]]:
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return False, b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(BASE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data, token, roleId)

    async def get_role_info(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> tuple[bool, Union[Dict, str]]:
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return False, b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(ROLE_DATA_URL, "POST", header, data=data)
        flag, res = await _check_response(raw_data, token, roleId)
        if flag and isinstance(res, Dict) and res.get("roleList") is None:
            return False, error_reply(WAVES_CODE_107)
        return flag, res

    async def get_tree(self) -> Union[Dict, int]:
        header = await get_headers()
        header.update({"wiki_type": "9"})
        data = {"devcode": ""}
        return await self._waves_request(WIKI_TREE_URL, "POST", header, data=data)

    async def get_wiki(self, catalogueId: str) -> tuple[bool, Union[Dict, str]]:
        header = await get_headers()
        header.update({"wiki_type": "9"})
        data = {"catalogueId": catalogueId, "limit": 1000}
        raw_data = await self._waves_request(WIKI_DETAIL_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_role_detail_info(
        self, charId: str, roleId: str, token: str, serverId: Optional[str] = None
    ) -> tuple[bool, Union[Dict, str]]:
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return False, b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "channelId": "19",
            "countryCode": "1",
            "id": charId,
        }
        raw_data = await self._waves_request(ROLE_DETAIL_URL, "POST", header, data=data)
        return await _check_response(raw_data, token)

    async def get_calabash_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> tuple[bool, Union[Dict, str]]:
        """数据坞"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return False, b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(
            CALABASH_DATA_URL, "POST", header, data=data
        )
        return await _check_response(raw_data, token, roleId)

    async def get_explore_data(
        self,
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
        countryCode: str = "1",
    ) -> tuple[bool, Union[Dict, str]]:
        """探索度"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return False, b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "countryCode": countryCode,
        }
        raw_data = await self._waves_request(
            EXPLORE_DATA_URL, "POST", header, data=data
        )
        return await _check_response(raw_data, token, roleId)

    async def get_challenge_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> tuple[bool, Union[Dict, str]]:
        """全息"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return False, b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(
            CHALLENGE_DATA_URL, "POST", header, data=data
        )
        return await _check_response(raw_data, token, roleId)

    async def get_abyss_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> Union[Dict, int]:
        """深渊"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(TOWER_DETAIL_URL, "POST", header, data=data)

    async def get_abyss_index(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> Union[Dict, int, str]:
        """深渊"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(TOWER_INDEX_URL, "POST", header, data=data)

    async def get_slash_index(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> Union[Dict, int, str]:
        """冥海"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        if header.get("roleId", "") != roleId:
            succ, b_at = await self.get_request_token(
                roleId, token, header.get("did", "")
            )
            if succ:
                header["b-at"] = b_at
            else:
                return b_at or error_reply(WAVES_CODE_990)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(SLASH_INDEX_URL, "POST", header, data=data)

    async def get_slash_detail(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ) -> Union[Dict, int]:
        """冥海"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(SLASH_DETAIL_URL, "POST", header, data=data)

    async def get_request_token(
        self, roleId: str, token: str, did: str, serverId: Optional[str] = None
    ) -> tuple[bool, str]:
        """请求token"""
        if roleId in self.bat_map:
            logger.debug(f"[{roleId}] 缓存读取bat成功: {self.bat_map[roleId]}")
            return True, self.bat_map[roleId]

        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update(
            {
                "token": token,
                # "Access-Control-Request-Header": "b-at,devcode,did,source,token",
                "did": did,
            }
        )
        header["b-at"] = ""
        # header.pop("X-Forwarded-For", None)
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(REQUEST_TOKEN, "POST", header, data=data)
        if isinstance(raw_data, dict) and (
            raw_data.get("code") == 200 or raw_data.get("code") == 10902
        ):
            content_data = raw_data.get("data")
            access_token = ""
            if isinstance(content_data, str):
                try:
                    json_data = json.loads(content_data)
                    access_token = json_data.get("accessToken", "")
                except Exception as e:
                    logger.error(f"[{roleId}] 获取token失败: {e}")
            elif isinstance(content_data, dict):
                access_token = content_data.get("accessToken", "")
            else:
                logger.error(f"[{roleId}] 获取token失败: {content_data}")

            if not access_token:
                return False, raw_data.get("msg", "") or ""
            else:
                self.bat_map[roleId] = access_token
                return True, access_token
        else:
            logger.warning(f"[{roleId}] 获取bat失败: {raw_data}")
            if isinstance(raw_data, dict):
                return False, raw_data.get("msg", "") or ""
            else:
                return False, ""

    async def calculator_refresh_data(
        self,
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
    ) -> tuple[bool, Union[Dict, str]]:
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(
            CALCULATOR_REFRESH_DATA_URL, "POST", header, data=data
        )
        return await _check_response(raw_data, token, roleId)

    @timed_async_cache(
        86400,
        lambda x: x[0] and isinstance(x[1], (dict, list)),
    )
    async def get_online_list_role(self, token: str) -> tuple[bool, Union[Dict, str]]:
        """所有的角色列表"""
        header = await get_headers(token)
        header.update({"token": token})
        data = {}
        raw_data = await self._waves_request(
            ONLINE_LIST_ROLE, "POST", header, data=data
        )
        return await _check_response(raw_data, token)

    @timed_async_cache(
        86400,
        lambda x: x[0] and isinstance(x[1], (dict, list)),
    )
    async def get_online_list_weapon(self, token: str) -> tuple[bool, Union[Dict, str]]:
        """所有的武器列表"""
        header = await get_headers(token)
        header.update({"token": token})
        data = {}
        raw_data = await self._waves_request(
            ONLINE_LIST_WEAPON, "POST", header, data=data
        )
        return await _check_response(raw_data, token)

    @timed_async_cache(
        86400,
        lambda x: x[0] and isinstance(x[1], (dict, list)),
    )
    async def get_online_list_phantom(
        self, token: str
    ) -> tuple[bool, Union[Dict, str]]:
        """所有的声骸列表"""
        header = await get_headers(token)
        header.update({"token": token})
        data = {}
        raw_data = await self._waves_request(
            ONLINE_LIST_PHANTOM, "POST", header, data=data
        )
        return await _check_response(raw_data, token)

    async def get_owned_role(
        self,
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
    ) -> tuple[bool, Union[Dict, str]]:
        """已拥有角色"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(
            QUERY_OWNED_ROLE, "POST", header, data=data
        )
        return await _check_response(raw_data, token)

    async def get_develop_role_cultivate_status(
        self,
        roleId: str,
        token: str,
        char_ids: List[str],
        serverId: Optional[str] = None,
    ) -> tuple[bool, Union[Dict, str]]:
        """角色培养状态"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "ids": ",".join(char_ids),
        }
        raw_data = await self._waves_request(
            ROLE_CULTIVATE_STATUS, "POST", header, data=data
        )
        return await _check_response(raw_data, token, roleId)

    async def get_batch_role_cost(
        self,
        roleId: str,
        token: str,
        content: List[Any],
        serverId: Optional[str] = None,
    ) -> tuple[bool, Union[Dict, str]]:
        """角色培养成本"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "content": json.dumps(content),
        }
        raw_data = await self._waves_request(BATCH_ROLE_COST, "POST", header, data=data)
        return await _check_response(raw_data, token, roleId)

    async def get_period_list(
        self,
        roleId: str,
        token: str,
    ) -> tuple[bool, Union[Dict, str]]:
        """资源简报列表"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        raw_data = await self._waves_request(PERIOD_LIST_URL, "GET", header)
        return await _check_response(raw_data, token, roleId)

    async def get_period_detail(
        self,
        type: Literal["month", "week", "version"],
        period: Union[str, int],
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
    ) -> tuple[bool, Union[Dict, str]]:
        """资源简报详情"""
        header = await get_headers(ck=token, queryRoleId=roleId)
        header.update({"token": token})
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "period": period,
        }
        if type == "month":
            url = MONTH_LIST_URL
        elif type == "week":
            url = WEEK_LIST_URL
        elif type == "version":
            url = VERSION_LIST_URL
        raw_data = await self._waves_request(url, "POST", header, data=data)
        return await _check_response(raw_data, token, roleId)

    async def get_gacha_log(
        self,
        cardPoolType: str,
        recordId: str,
        roleId: str,
        serverId: Optional[str] = None,
    ):
        """抽卡记录"""
        header = {"Content-Type": "application/json;charset=UTF-8"}
        data = {
            "playerId": roleId,
            "cardPoolType": cardPoolType,
            "serverId": self.get_server_id(roleId, serverId),
            "languageCode": "zh-Hans",
            "recordId": recordId,
        }
        url = GACHA_NET_LOG_URL if self.is_net(roleId) else GACHA_LOG_URL
        return await self._waves_request(url, "POST", header, json_data=data)

    async def get_ann_list_by_type(
        self, eventType: str = "", pageSize: Optional[int] = None
    ):
        """获取公告列表"""
        data: Dict[str, Any] = {"gameId": GAME_ID}
        if eventType:
            data.update({"eventType": eventType})
        if pageSize:
            data.update({"pageSize": pageSize})
        headers = await get_headers()
        return await self._waves_request(ANN_LIST_URL, "POST", headers, data=data)

    async def get_ann_detail(self, post_id: str):
        """获取公告详情"""
        if post_id in self.ann_map:
            return self.ann_map[post_id]

        headers = await get_headers()
        headers.update({"token": "", "devcode": ""})
        data = {"isOnlyPublisher": 1, "postId": post_id, "showOrderType": 2}
        res = await self._waves_request(ANN_CONTENT_URL, "POST", headers, data=data)
        if isinstance(res, dict) and res.get("code") == 200:
            self.ann_map[post_id] = res["data"]["postDetail"]
            return res["data"]["postDetail"]
        return {}

    async def get_ann_list(self, is_cache: bool = False):
        """获取公告列表"""
        if is_cache and self.ann_list_data:
            return self.ann_list_data

        self.ann_list_data = []
        for _event in self.event_type.keys():
            res = await self.get_ann_list_by_type(eventType=_event, pageSize=5)
            if isinstance(res, dict) and res.get("code") == 200:
                value = [{**x, "id": int(x["id"])} for x in res["data"]["list"]]
                self.ann_list_data.extend(value)

        return self.ann_list_data

    async def get_wiki_home(self):
        """获取wiki首页"""
        headers = await get_headers()
        headers.update({"wiki_type": "9"})
        res = await self._waves_request(WIKI_HOME_URL, "POST", headers)
        if isinstance(res, dict) and res.get("code") == 200:
            return res
        return {}

    async def get_entry_detail(self, entry_id: str):
        """获取entry详情"""
        if entry_id in self.entry_detail_map:
            return self.entry_detail_map[entry_id]

        headers = await get_headers()
        headers.update({"wiki_type": "9"})
        data = {"id": entry_id}
        res = await self._waves_request(
            WIKI_ENTRY_DETAIL_URL, "POST", headers, data=data
        )
        if isinstance(res, dict) and res.get("code") == 200:
            self.entry_detail_map[entry_id] = res
            return res
        return {}

    async def login(self, mobile: int | str, code: str, did: str):
        platform = login_platform()
        header = await get_headers(platform=platform)
        data = {
            "mobile": mobile,
            "code": code,
            "devCode": did,
        }
        if platform == "h5":
            url = LOGIN_H5_URL
        else:
            url = LOGIN_URL
        return await self._waves_request(url, "POST", header, data=data)

    async def _waves_request(
        self,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        header=None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> Union[Dict, int]:
        if header is None:
            header = await get_headers()
        if header:
            header.pop("roleId", None)

        proxy_func = get_need_proxy_func()
        if inspect.stack()[1].function in proxy_func or "all" in proxy_func:
            proxy_url = get_local_proxy_url()
        else:
            proxy_url = None

        async def do_request(req_data, client_session):
            async with client_session.request(
                method,
                url=url,
                headers=header,
                params=params,
                json=json_data,
                data=req_data,
                proxy=proxy_url,
                timeout=ClientTimeout(total=10),
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
                        raw_data["data"] = json.loads(raw_data["data"])
                    except Exception:
                        pass

                logger.debug(
                    f"url:[{url}] params:[{params}] headers:[{header}] data:[{req_data}] raw_data:{raw_data}"
                )
                return raw_data

        async def solve_captcha():
            if not self.captcha_solver:
                return
            for _ in range(max_retries):
                try:
                    return await self.captcha_solver.solve()
                except CaptchaError as e:
                    logger.error(f"url:[{url}] 验证码破解失败: {e}")

            return {"code": WAVES_CODE_999, "data": "验证码破解失败"}

        for attempt in range(max_retries):
            try:
                client = await self.get_session(proxy=proxy_url)
                if not client:
                    logger.warning(f"url:[{url}] 获取session失败")
                    continue

                response = await do_request(data, client)

                res_data = response.get("data", {})
                if (
                    self.captcha_solver
                    and isinstance(res_data, dict)
                    and res_data.get("geeTest") is True
                ):
                    seccode_data = await solve_captcha()
                    if isinstance(seccode_data, CaptchaResult):
                        seccode_data = seccode_data.model_dump_json()

                    if isinstance(seccode_data, dict):
                        seccode_data = json.dumps(seccode_data)

                    # 重试数据准备
                    retry_data = data.copy() if data else {}
                    retry_data["geeTestData"] = seccode_data
                    return await do_request(retry_data, client)

                return response

            except aiohttp.ClientError as e:
                logger.warning(f"url:[{url}] 网络请求失败, 尝试次数 {attempt + 1}", e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
            except Exception as e:
                logger.warning(f"url:[{url}] 发生未知错误, 尝试次数 {attempt + 1}", e)
                return {"code": WAVES_CODE_999, "data": f"请求时发生未知错误: {e}"}

        return {"code": WAVES_CODE_999, "data": "请求服务器失败，已达最大重试次数"}
