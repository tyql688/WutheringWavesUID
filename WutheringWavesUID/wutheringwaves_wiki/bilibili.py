import copy
import time
from typing import Union, List

import httpx
from bs4 import BeautifulSoup

from gsuid_core.utils.image.image_tools import get_pic
from ..utils.resource.RESOURCE_PATH import GUIDE_CONFIG_MAP
from ..utils.util import generate_random_string

BBS_LIST = "https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space"
w_webid = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzcG1faWQiOiIwLjAiLCJidXZpZCI6IkNGNDFBQjUyLTRBNDAtOUU3My0wQzQyLUNFMUI5OTcyNzU2MDE5NTkxaW5mb2MiLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKE1hY2ludG9zaDsgSW50ZWwgTWFjIE9TIFggMTBfMTVfNykgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyOC4wLjAuMCBTYWZhcmkvNTM3LjM2IEVkZy8xMjguMC4wLjAiLCJidXZpZF9mcCI6IjJlZDhjNDg1YzliZWFlMzM0MzJlZjEyNTNkZjM0OTQ5IiwiY3JlYXRlZF9hdCI6MTcyODE0NDI4MywidHRsIjo4NjQwMCwidXJsIjoiLzQ4NzI3NTAyNy9hcnRpY2xlIiwicmVzdWx0Ijoibm9ybWFsIiwiaXNzIjoiZ2FpYSIsImlhdCI6MTcyODE0NDI4M30.lziDx5S0Kra6-FeJhumVTs77nMYebzN0XIAKPQtBNBcIR5Gm47QN4gd1CAFfktSEBtvdZQeFGxrCXT3JURVYpbb0TDjqk-hKaJ1w1Lxi5liJ9B8-GVUVK4t4CZ4ownMFH241j259lKQ0Z9ywUdHv4bJDuZ2ilD1qiU8oEo2FCKPJ7yS6n0-Le4qbaUBUgpCy93RC3-_4n9VUOHZB_YS3Krd9tF-I_vkQdf57f8P3QoGl5gxDeNlwWWZ4g7aTIOb6aC7rInwelqI65nDSe4TK2JOgUkmVlgPc_2LPt0ZZgBUwrYF5E16E5l9jckGRm2s55jxqz3_TRxdJiOwu8eyfMg"
web_location = 333.999


class GuideBilibili:
    _headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
    }

    async def get_bbs_list(self, auther_id: int, page: int, offset: str = None):
        headers = copy.deepcopy(self._headers)
        headers['content-type'] = "application/json; charset=utf-8"
        params = {
            "host_mid": auther_id,
            "page": page,
            "wts": int(time.time()),
            "w_webid": w_webid,
            "web_location": web_location,
            "w_rid": generate_random_string()
        }
        if offset:
            params['offset'] = offset
        async with httpx.AsyncClient(timeout=None) as client:
            return await client.get(BBS_LIST, headers=headers, params=params, timeout=10)

    async def get_bbs_detail(self, jump_url):
        headers = copy.deepcopy(self._headers)
        headers['content-type'] = "text/html,application/xhtml+xml,application/xml"
        async with httpx.AsyncClient(timeout=None) as client:
            return await client.get(jump_url, headers=headers, timeout=10)

    async def get_guide_all_moment(self, auther_id: int):
        result = []
        page = 1
        offset = None
        while True:
            res = await self.get_bbs_list(auther_id, page, offset)
            if res.status_code != 200:
                return None

            data = res.json()
            if not data['data']['items']:
                return None

            for item in data['data']['items']:
                jump_url = item['jump_url']
                if jump_url.startswith('//'):
                    jump_url = 'https:' + jump_url
                result.append((item['content'], jump_url))

            has_more = data['data']['has_more']
            offset = data['data']['offset']
            page += 1
            if not has_more or not offset:
                break

        return result

    async def get_ann_detail_pic(self, href: str, auther_id: int):
        response = await self.get_bbs_detail(href)

        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找所有具有特定类名的div标签
        div_tags = soup.find_all("div", class_="bili-album__preview__picture")

        # 遍历所有找到的div标签，并从中提取img标签的src属性
        image_urls = []
        for div_tag in div_tags:
            if (img_tag := div_tag.find("img")) and img_tag.get("src"):
                url = img_tag["src"].split('@')[0]
                if img_tag["src"].startswith('//'):
                    url = 'https:' + url
                image_urls.append(url)
        result = []
        if auther_id == GUIDE_CONFIG_MAP['金铃子攻略组'][1]:
            for url in image_urls:
                img = await get_pic(url)
                if img.size[1] < 6000:
                    continue
                result.append(url)
        else:
            result = image_urls
        return result

    async def get(self, role_name: str, auther_id: int) -> Union[List[str], None]:
        all_moment = await self.get_guide_all_moment(auther_id)
        monent = None
        for title, monent_temp in all_moment:
            if '·' in role_name:
                name_split = role_name.split('·')
                if all(fragment in title for fragment in name_split):
                    monent = monent_temp
                    break
            elif role_name in title and '一图流' in title:
                monent = monent_temp
                break

        if not monent:
            return None

        return await self.get_ann_detail_pic(monent, auther_id)
