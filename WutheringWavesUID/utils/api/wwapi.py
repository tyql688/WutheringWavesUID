from typing import List, Optional

from pydantic import BaseModel, Field

MAIN_URL = "https://top.camellya.xyz"
# MAIN_URL = "http://127.0.0.1:9001"

UPLOAD_URL = f"{MAIN_URL}/top/waves/upload"
GET_RANK_URL = f"{MAIN_URL}/top/waves/rank"
ONE_RANK_URL = f"{MAIN_URL}/top/waves/one"


class RankDetail(BaseModel):
    rank: int
    user_id: str
    username: str
    alias_name: str
    kuro_name: str
    waves_id: str
    char_id: int
    level: int
    chain: int
    weapon_id: int
    weapon_level: int
    weapon_reson_level: int
    sonata_name: str
    phantom_score: float
    phantom_score_bg: str
    expected_damage: float
    expected_name: str


class RankInfoData(BaseModel):
    details: List[RankDetail]
    page: int
    page_num: int


class RankInfoResponse(BaseModel):
    code: int
    message: str
    data: RankInfoData


class RankItem(BaseModel):
    char_id: int
    page: int
    page_num: int
    rank_type: int
    waves_id: Optional[str] = ""


class OneRankRequest(BaseModel):
    char_id: int = Field(..., description="角色ID")
    waves_id: Optional[str] = Field(default="", description="鸣潮ID")


class OneRankResponse(BaseModel):
    code: int
    message: str
    data: List[RankDetail]
