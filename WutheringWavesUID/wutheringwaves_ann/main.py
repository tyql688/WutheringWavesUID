import asyncio
import copy

import httpx

from gsuid_core.logger import logger

from ..utils.api.api import ANN_CONTENT_URL, ANN_LIST_URL, GAME_ID


class _Dict(dict):
    __setattr__ = dict.__setitem__  # type: ignore
    __getattr__ = dict.__getitem__


class ann:
    _headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "version": "2.4.3",
    }
    ann_list_data = []
    ann_content_data = {}
    event_type = {"2": "资讯", "3": "公告", "1": "活动"}
    today = 0

    async def _get_ann_list(self, eventType: str = "", pageSize: int = None):
        data = {"gameId": GAME_ID}
        if eventType:
            data.update({"eventType": eventType})
        if pageSize:
            data.update({"pageSize": pageSize})
        headers = copy.deepcopy(self._headers)
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.post(
                ANN_LIST_URL, headers=headers, data=data, timeout=10
            )
            value = res.json(object_hook=_Dict)
            logger.debug(f"公告数据查询: {value}")
            return value

    async def _get_ann_detail(self, post_id: int):
        headers = copy.deepcopy(self._headers)
        headers.update(
            {
                "devcode": "",
                "token": "",
            }
        )
        data = {"isOnlyPublisher": 1, "postId": post_id, "showOrderType": 2}
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.post(
                ANN_CONTENT_URL, headers=headers, data=data, timeout=10
            )
            return res.json(object_hook=_Dict)

    async def get_ann_detail(self, post_id: int):
        res = await self._get_ann_detail(post_id)
        if res.code == 200:
            self.ann_content_data = res.data.postDetail
        return self.ann_content_data

    async def get_ann_list(self):
        self.ann_list_data = []
        for _event in self.event_type.keys():
            res = await self._get_ann_list(eventType=_event, pageSize=5)
            if res.code == 200:
                value = [{**x, "id": int(x["id"])} for x in res.data.list]
                self.ann_list_data.extend(value)

            await asyncio.sleep(1)

        return self.ann_list_data

    async def get_ann_ids(self):
        await self.get_ann_list()
        if not self.ann_list_data:
            return []
        return [x["id"] for x in self.ann_list_data]
