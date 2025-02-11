import copy
from typing import List, Union

import httpx
from bs4 import BeautifulSoup

from gsuid_core.plugins.WutheringWavesUID.WutheringWavesUID.utils.resource.RESOURCE_PATH import (
    GUIDE_CONFIG_MAP,
)
from gsuid_core.utils.image.image_tools import get_pic

TAP_URL = "https://www.taptap.cn"
BBS_LIST = f"{TAP_URL}/user/[id]"
PAGE_SIZE_MAX = 10


class GuideTap:
    _headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    }

    async def get_bbs_list(self, auther_id: int, page: int = 1):
        headers = copy.deepcopy(self._headers)
        url = BBS_LIST.replace("[id]", str(auther_id))
        if page > 1:
            url = url + f"?page={page}"

        async with httpx.AsyncClient(timeout=None) as client:
            return await client.get(url, headers=headers, timeout=10)

    async def get_bbs_detail(self, href):
        headers = copy.deepcopy(self._headers)
        url = TAP_URL + href
        async with httpx.AsyncClient(timeout=None) as client:
            return await client.get(url, headers=headers, timeout=10)

    async def get_guide_all_moment(self, auther_id: int):
        result = {}

        for i in range(1, PAGE_SIZE_MAX):
            response = await self.get_bbs_list(auther_id, i)
            soup = BeautifulSoup(response.text, "html.parser")
            # 查找所有匹配的span标签
            span_tags = soup.find_all(
                "span",
                {"class": "moment-article__summary--title paragraph-m16-w16 font-bold"},
            )
            # 查找所有匹配的a标签
            a_tags = soup.find_all(
                "a", {"class": "tap-router moment-article__image-list"}
            )

            for span_tag, a_tag in zip(span_tags, a_tags):
                result[span_tag.text] = a_tag["href"]

        return result

    async def get_ann_detail_pic(self, href: str, auther_id: int):
        response = await self.get_bbs_detail(href)
        soup = BeautifulSoup(response.text, "html.parser")
        # 查找所有具有特定类名的div标签
        div_tags = soup.find_all("div", class_="content-image__image")

        # 遍历所有找到的div标签，并从中提取img标签的src属性
        image_urls = [
            img_tag["src"]
            for div_tag in div_tags
            if (img_tag := div_tag.find("img")) and img_tag.get("src")
        ]

        result = []
        # logger.info(f'{auther_id}获取到图片数量为{len(image_urls)}')
        if auther_id == GUIDE_CONFIG_MAP["Moealkyne"][1]:
            for url in image_urls:
                img = await get_pic(url)
                if img.size[1] < 8000:
                    continue
                result.append(url)
        else:
            result = image_urls
        return result

    async def get(self, role_name: str, auther_id: int) -> Union[List[str], None]:
        all_moment = await self.get_guide_all_moment(auther_id)
        # logger.info(f'{auther_id}获取到动态数量为{len(all_moment)}')
        monent = None
        for title, monent_temp in all_moment.items():
            if "·" in role_name:
                name_split = role_name.split("·")
                if all(fragment in title for fragment in name_split):
                    monent = monent_temp
                    break
            elif role_name in title and "一图流" in title:
                monent = monent_temp
                break

        if not monent:
            return

        return await self.get_ann_detail_pic(monent, auther_id)
