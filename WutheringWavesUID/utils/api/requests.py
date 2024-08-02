import copy
from typing import Any, Dict, Union, Literal, Optional

from aiohttp import FormData, TCPConnector, ClientSession, ContentTypeError

from gsuid_core.logger import logger
from .api import GAME_DATA_URL, BASE_DATA_URL, ROLE_DATA_URL, GAME_ID


async def _check_response(res: Dict) -> (bool, Union[Dict, str]):
    if res and res.get('code') == 200 and res.get('data'):
        return True, res['data']

    if res and res.get('msg'):
        return False, res['msg']

    return False, '查查日志吧~'


class WavesApi:
    ssl_verify = True
    _HEADER = {
        "source": "android",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    async def get_game_info(self, token: str) -> (bool, Union[Dict, str]):
        header = copy.deepcopy(self._HEADER)
        header.update({'token': token})
        raw_data = await self._waves_request(GAME_DATA_URL, "POST", header)
        return await _check_response(raw_data)

    async def get_account_info(self, serverId: str, roleId: str, token: str) -> (bool, Union[Dict, str]):
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
                    raw_data = {"code": -999, "data": _raw_data}
                logger.debug(raw_data)
                return raw_data
