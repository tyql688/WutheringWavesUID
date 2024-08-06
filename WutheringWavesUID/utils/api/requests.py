import copy
from datetime import datetime
from typing import Any, Dict, Union, Literal, Optional, List

from aiohttp import FormData, TCPConnector, ClientSession, ContentTypeError

from gsuid_core.logger import logger
from .api import *
from ..error_reply import ERROR_CODE, WAVES_CODE_100, WAVES_CODE_200, WAVES_CODE_998, WAVES_CODE_999


async def _check_response(res: Dict) -> (bool, Union[Dict, str]):
    if isinstance(res, dict):
        if res.get('code') == 200 and res.get('data'):
            return True, res['data']

        if res.get('msg'):
            return False, res['msg']
    return False, ERROR_CODE[WAVES_CODE_999]


class WavesApi:
    ssl_verify = True
    _HEADER = {
        "source": "android",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    async def get_active_list(self) -> (bool, Union[Dict, str]):
        """活动"""
        header = copy.deepcopy(self._HEADER)
        header.update({'gameId': GAME_ID})
        raw_data = await self._waves_request(EVENT_LIST_URL, "POST", header)
        return await _check_response(raw_data)

    async def get_kuro_role_info(self, token: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        raw_data = await self._waves_request(KURO_ROLE_URL, "POST", header)
        return await _check_response(raw_data)

    async def get_game_role_info(self, token: str, gameId: str = 3) -> (bool, Union[Dict, str]):
        succ, data = await self.get_kuro_role_info(token)
        if not succ:
            return succ, data
        for role in data['defaultRoleList']:
            if role['gameId'] == gameId:
                return True, role
        return False, WAVES_CODE_100

    async def get_daily_info(self, token: str) -> (bool, Union[Dict, str]):
        """每日"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        raw_data = await self._waves_request(GAME_DATA_URL, "POST", header)
        return await _check_response(raw_data)

    async def refresh_data(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
        """刷新数据"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(REFRESH_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_base_info(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(BASE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_role_info(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(ROLE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_role_detail_info(self, serverId: str, roleId: str, token: str, id: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId, 'id': id}
        raw_data = await self._waves_request(ROLE_DETAIL_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_calabash_data(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
        """数据坞"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(CALABASH_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_explore_data(
            self,
            serverId: str,
            roleId: str,
            token: str,
            countryCode: str = "1"
    ) -> (bool, Union[Dict, str]):
        """探索度"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId, 'countryCode': countryCode}
        raw_data = await self._waves_request(EXPLORE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_challenge_data(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
        """全息"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(CHALLENGE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_challenge_index(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
        """全息"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID,
                'serverId': serverId,
                'roleId': roleId}
        raw_data = await self._waves_request(CHALLENGE_INDEX_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def sign_in(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
        """签到"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token, 'devcode': ''})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId, 'reqMonth': f"{datetime.now().month:02}"}
        return await self._waves_request(SIGNIN_URL, "POST", header, data=data)
        # return await _check_response(raw_data)

    async def _waves_request(
            self,
            url: str,
            method: Literal["GET", "POST"] = "GET",
            header=None,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[FormData] = None,
    ) -> Union[Dict, int]:

        if header is None:
            header = self._HEADER

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
                logger.debug(raw_data)
                return raw_data


class TapApi:
    ssl_verify = True
    _DEFAULT_DATA = {
        'app_id': TAP_WAVES_APP_ID,
        'X-UA': TAP_UA
    }
    _HEADER = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": TAP_USER_AGENT
    }

    async def get_waves_id_by_tap(self, tapUserId: int) -> int:
        data = copy.deepcopy(self._DEFAULT_DATA)
        data.update({'user_id': tapUserId})
        raw_data = await self._tap_request(USER_DETAIL, "GET", None, params=data)
        valid_data = raw_data.get('data', {})
        if not isinstance(valid_data, dict):
            return WAVES_CODE_998

        # 检查是否绑定
        bind = valid_data.get('is_bind', False)
        if not bind:
            return WAVES_CODE_200

        # 获取角色 ID
        role_info = next((item for item in valid_data.get('list', []) if 'basic_module' in item), None)
        subtitle = role_info['basic_module']['subtitle'] if role_info else None
        role_id = subtitle.split("ID:")[1]
        logger.debug(f"TapTap : {tapUserId}, 获取到鸣潮角色ID: {role_id}")
        return int(role_id)

    async def get_all_role_info(self, tapUserId: int, roleNum: int = 100) -> Union[List, None]:
        data = copy.deepcopy(self._DEFAULT_DATA)
        data.update({'user_id': tapUserId, 'form': 0, 'limit': roleNum, })
        raw_data = await self._tap_request(CHAR_DETAIL, "GET", None, params=data)
        if not raw_data:
            return
        return raw_data.get('data', {}).get('list', None)

    async def _tap_request(
            self,
            url: str,
            method: Literal["GET", "POST"] = "GET",
            header=None,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[FormData] = None,
    ) -> Union[Dict, int]:

        if header is None:
            header = self._HEADER

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
                logger.debug(raw_data)
                return raw_data
