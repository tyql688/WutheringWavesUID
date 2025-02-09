from typing import Dict
from pathlib import Path

from ..utils.api.requests import Wiki
from ..utils.api.api import WIKI_CATALOGUE_MAP

TEXT_PATH = Path(__file__).parent / "texture2d"
QUERY_ROLE_TYPE = {
    "命座": "1",
    "天赋": "2",
}


async def draw_wiki_detail(query_type: str, name: str):
    noi = f"[鸣潮] 暂无【{name}】对应{query_type}wiki"
    if query_type not in WIKI_CATALOGUE_MAP:
        return noi

    res = await Wiki().get_entry_detail_by_name(name, WIKI_CATALOGUE_MAP[query_type])
    if not res:
        return noi

    if query_type == "武器":
        return await draw_wiki_weapon(name, res["data"])
    elif query_type == "声骸":
        return await draw_wiki_echo(name, res["data"])


async def draw_wiki_weapon(name: str, raw_data: Dict):
    pass


async def draw_wiki_echo(name: str, raw_data: Dict):
    pass
