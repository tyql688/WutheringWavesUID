import copy

import httpx

from ..utils.api.api import BBS_LIST, ANN_CONTENT_URL


class _Dict(dict):
    __setattr__ = dict.__setitem__  # type: ignore
    __getattr__ = dict.__getitem__


class Guide:
    _headers = {
        "source": "h5",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    async def get_bbs_list(
        self,
        auther_id: int,
        type: int = 2,
        searchType: int = 1,
        pageIndex: int = 1,
        pageSize: int = 99
    ):
        headers = copy.deepcopy(self._headers)
        data = {
            'otherUserId': auther_id,
            'type': type,
            'searchType': searchType,
            'pageIndex': pageIndex,
            'pageSize': pageSize
        }
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.post(BBS_LIST, headers=headers, data=data, timeout=10)
            return res.json(object_hook=_Dict)

    async def _get_ann_detail(self, post_id: int | str):
        headers = copy.deepcopy(self._headers)
        headers.update({"devcode": "", "token": "", })
        data = {
            'isOnlyPublisher': 1,
            'postId': post_id,
            'showOrderType': 2
        }
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.post(ANN_CONTENT_URL, headers=headers, data=data, timeout=10)
            return res.json(object_hook=_Dict)

    async def get_guide_data(self, auther_id: int):
        res = await self.get_bbs_list(auther_id)
        if res.code == 200:
            return res.data.postList

    async def get_ann_detail(self, post_id: int | str):
        res = await self._get_ann_detail(post_id)
        if res.code == 200:
            return res.data.postDetail
