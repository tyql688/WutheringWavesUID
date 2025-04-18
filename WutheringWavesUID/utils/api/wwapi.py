from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

MAIN_URL = "https://top.camellya.xyz"
# MAIN_URL = "http://127.0.0.1:9001"

UPLOAD_URL = f"{MAIN_URL}/top/waves/upload"
GET_RANK_URL = f"{MAIN_URL}/top/waves/rank"
ONE_RANK_URL = f"{MAIN_URL}/top/waves/one"
UPLOAD_ABYSS_RECORD_URL = f"{MAIN_URL}/top/waves/abyss/upload"
GET_ABYSS_RECORD_URL = f"{MAIN_URL}/top/waves/abyss/record"
GET_HOLD_RATE_URL = f"{MAIN_URL}/api/waves/hold/rates"
GET_POOL_LIST = f"{MAIN_URL}/api/waves/pool/list"
GET_TOWER_APPEAR_RATE = f"{MAIN_URL}/api/waves/abyss/appear_rate"

ABYSS_TYPE = Literal["l4", "m2", "r4", "a"]

ABYSS_TYPE_MAP = {
    "残响之塔": "l",
    "深境之塔": "m",
    "回音之塔": "r",
}

ABYSS_TYPE_MAP_REVERSE = {
    "l4": "残响之塔 - 4层",
    "m2": "深境之塔 - 2层",
    "r4": "回音之塔 - 4层",
}


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


# ------------------------------------------------------------
# 深渊记录
# ------------------------------------------------------------


class AbyssDetail(BaseModel):
    area_type: ABYSS_TYPE
    area_name: str
    floor: int
    char_ids: List[int]


class AbyssItem(BaseModel):
    waves_id: str
    abyss_record: List[AbyssDetail]


class AbyssRecordRequest(BaseModel):
    abyss_type: ABYSS_TYPE


class AbyssUseRate(BaseModel):
    char_id: int
    rate: float


class AbyssRecord(BaseModel):
    abyss_type: ABYSS_TYPE
    use_rate: List[AbyssUseRate]


class AbyssRecordResponse(BaseModel):
    code: int
    message: str
    data: List[AbyssRecord]


# ------------------------------------------------------------
# 角色持有率


class RoleHoldRate(BaseModel):
    char_id: int
    rate: float
    chain_rate: Dict[int, float]


class RoleHoldRateRequest(BaseModel):
    char_id: Optional[int] = None


class RoleHoldRateResponse(BaseModel):
    code: int
    message: str
    data: List[RoleHoldRate]
