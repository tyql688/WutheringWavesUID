import copy
import re
from typing import Union, List

import httpx

from ..utils.api.api import BBS_LIST, ANN_CONTENT_URL
from ..utils.resource.RESOURCE_PATH import GUIDE_CONFIG_MAP


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

    async def _get_ann_detail(self, post_id: Union[int, str]):
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

    async def get_ann_detail(self, post_id: Union[int, str]):
        res = await self._get_ann_detail(post_id)
        if res.code == 200:
            return res.data.postDetail

    async def get(self, role_name: str, auther_id: int) -> Union[List[str], None]:
        all_bbs_data = await self.get_guide_data(auther_id)
        if not all_bbs_data:
            return

        post_id = None
        for i in all_bbs_data:
            post_title = i['postTitle']
            if '·' in role_name:
                name_split = role_name.split('·')
                if all(fragment in post_title for fragment in name_split):
                    post_id = i['postId']
                    break
            elif await self.check_title(role_name, post_title, auther_id):
                post_id = i['postId']
                break

        if not post_id:
            return

        res = await self.get_ann_detail(post_id)
        if not res:
            return

        result = []
        for index, _temp in enumerate(res['postContent']):
            if _temp['contentType'] != 2:
                continue
            _msg = re.search(r'(https://.*[png|jpg])', _temp['url'])
            url = _msg.group(0) if _msg else ''

            if await self.check_width(_temp['imgWidth'], _temp['imgHeight'], auther_id):
                continue

            if url:
                result.append(url)

        return result

    async def check_width(self, imgWidth: int, imgHeight: int, auther_id: int) -> bool:
        if GUIDE_CONFIG_MAP['結星'][1] == auther_id:
            # 結星
            return imgHeight < 2500
        elif GUIDE_CONFIG_MAP['XMu'][1] == auther_id:
            # XMu
            return imgWidth < 1910
        else:
            return True

    async def check_title(self, role_name: str, post_title: str, auther_id: int) -> bool:
        if role_name in post_title and '一图流' in post_title:
            return True
        if GUIDE_CONFIG_MAP['結星'][1] == auther_id and role_name in post_title and '攻略' in post_title:
            return True
        return False
