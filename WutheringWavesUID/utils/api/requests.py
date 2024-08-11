import copy
import uuid
from datetime import datetime
from typing import Any, Dict, Union, Literal, Optional

from aiohttp import FormData, TCPConnector, ClientSession, ContentTypeError

from gsuid_core.logger import logger
from .api import *
from ..error_reply import ERROR_CODE, WAVES_CODE_100, WAVES_CODE_999


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

    async def refresh_data(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        """刷新数据"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(REFRESH_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_base_info(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(BASE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_role_info(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(ROLE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_wiki(self, catalogueId: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'wiki_type': '9'})
        data = {'catalogueId': catalogueId, 'limit': 1000}
        raw_data = await self._waves_request(WIKI_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_role_detail_info(self, charId: str, roleId: str, token: str, serverId: str = SERVER_ID) -> (
        bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId, 'id': charId}
        raw_data = await self._waves_request(ROLE_DETAIL_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_calabash_data(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        """数据坞"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(CALABASH_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_explore_data(
        self,
        roleId: str,
        token: str,
        serverId: str = SERVER_ID,
        countryCode: str = "1"
    ) -> (bool, Union[Dict, str]):
        """探索度"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId, 'countryCode': countryCode}
        raw_data = await self._waves_request(EXPLORE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_challenge_data(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        """全息"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(CHALLENGE_DATA_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_challenge_index(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        """全息"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(CHALLENGE_INDEX_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_tower_data(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        """深渊"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(TOWER_DETAIL_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def get_tower_index(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        """深渊"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId}
        raw_data = await self._waves_request(TOWER_INDEX_URL, "POST", header, data=data)
        return await _check_response(raw_data)

    async def sign_in(self, roleId: str, token: str, serverId: str = SERVER_ID) -> (bool, Union[Dict, str]):
        """签到"""
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token, 'devcode': ''})
        data = {'gameId': GAME_ID, 'serverId': serverId, 'roleId': roleId, 'reqMonth': f"{datetime.now().month:02}"}
        return await self._waves_request(SIGNIN_URL, "POST", header, data=data)
        # return await _check_response(raw_data)

    async def get_gacha_log(self, cardPoolType: str, recordId: str, roleId: str, serverId: str = SERVER_ID):
        """抽卡记录"""
        header = {"Content-Type": "application/json;charset=UTF-8"}
        data = {
            "playerId": roleId,
            "cardPoolType": cardPoolType,
            "serverId": serverId,
            "languageCode": "zh-Hans",
            "recordId": recordId
        }
        return await self._waves_request(GACHA_LOG_URL, "POST", header, json=data)

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


class KuroLogin:
    ssl_verify = True
    _HEADER = {
        "source": "android",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    async def login(self, mobile: int, code: str):
        header = copy.deepcopy(self._HEADER)
        data = {"mobile": mobile, "code": code, "devCode": str(uuid.uuid4()).upper()}
        return await self._kuro_request(LOGIN_URL, "POST", header, data=data)

    async def send_phone_code(
        self,
        mobile: int,
        override_geetest: Dict = None,
    ):
        header = copy.deepcopy(self._HEADER)
        header.update({"devCode": str(uuid.uuid4()).upper()})

        data = {
            "mobile": mobile,
            "geeTestData": ""
        }
        if override_geetest:
            data['geeTestData'] = override_geetest

        response = await self._kuro_request(KURO_GET_CODE_URL, "POST", header, data=data)
        if response.get('code') == 200 & response.get('data'):
            geeTest = response.get('data', {}).get("geeTest", False)
            pass

    async def _kuro_request(
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
