from typing import List, Union

from msgspec import UNSET, Struct, UnsetType, field
from pydantic import BaseModel


class GeneralGeetestData(Struct):
    geetest_challenge: str
    geetest_seccode: str
    geetest_validate: str


class GeneralV1SendPhoneCodeRequest(Struct):
    phone: str
    type: int
    captcha: Union[GeneralGeetestData, UnsetType] = field(default=UNSET)


class EnergyData(BaseModel):
    """结晶波片"""
    name: str
    img: str
    refreshTimeStamp: int
    cur: int
    total: int


class LivenessData(BaseModel):
    """活跃度"""
    name: str
    img: str
    cur: int
    total: int


class BattlePassData(BaseModel):
    """电台"""
    name: str
    cur: int
    total: int


class DailyData(BaseModel):
    """每日数据"""
    gameId: int
    userId: int
    serverId: str
    roleId: str
    roleName: str
    signInTxt: str
    hasSignIn: bool
    energyData: EnergyData
    livenessData: LivenessData
    battlePassData: List[BattlePassData]


class Role(BaseModel):
    roleId: int
    level: int
    roleName: str
    roleIconUrl: str
    rolePicUrl: str
    starLevel: int
    attributeId: int
    attributeName: str
    weaponTypeId: int
    weaponTypeName: str
    acronym: str
    # mapRoleId: int | None


class RoleList(BaseModel):
    roleList: List[Role]


class Box(BaseModel):
    boxName: str
    num: int


class AccountBaseInfo(BaseModel):
    name: str
    id: int
    creatTime: int
    activeDays: int
    level: int
    worldLevel: int
    roleNum: int
    soundBox: int
    energy: int
    maxEnergy: int
    liveness: int
    livenessMaxCount: int
    livenessUnlock: bool
    chapterId: int
    bigCount: int
    smallCount: int
    achievementCount: int
    boxList: list[Box]
    showToGuest: bool


class Chain(BaseModel):
    name: str
    order: int
    description: str
    iconUrl: str
    unlocked: bool


class Weapon(BaseModel):
    weaponId: int
    weaponName: str
    weaponType: int
    weaponStarLevel: int
    weaponIcon: str
    weaponEffectName: str
    effectDescription: str


class PhantomProp(BaseModel):
    phantomPropId: int
    name: str
    phantomId: int
    quality: int
    cost: int
    iconUrl: str
    skillDescription: str


class FetterDetail(BaseModel):
    groupId: int
    name: str
    iconUrl: str
    num: int
    firstDescription: str
    secondDescription: str


class EquipPhantom(BaseModel):
    phantomProp: PhantomProp
    cost: int
    quality: int
    level: int
    fetterDetail: FetterDetail


class Skill(BaseModel):
    id: int
    type: str
    name: str
    description: str
    iconUrl: str


class PhantomData(BaseModel):
    cost: int
    equipPhantomList: List[EquipPhantom]


class RoleDetailData(BaseModel):
    role: Role
    level: int
    chainList: List[Chain]
    weaponData: Weapon
    phantomData: PhantomData
    skillList: List[Skill]


class KuroRoleInfo(BaseModel):
    id: int
    userId: int
    gameId: int
    serverId: str
    serverName: str
    roleId: str
    roleName: str
    gameHeadUrl: str
    roleNum: int
    achievementCount: int


class GachaLog(BaseModel):
    cardPoolType: str
    resourceId: int
    qualityLevel: int
    resourceType: str
    name: str
    count: int
    time: str

    def __hash__(self):
        return hash((self.resourceId, self.time))
