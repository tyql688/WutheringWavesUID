from typing import List, Union, Optional, Any, Dict

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
    breach: Optional[int]
    roleName: str
    roleIconUrl: Optional[str]
    rolePicUrl: Optional[str]
    starLevel: int
    attributeId: int
    attributeName: Optional[str]
    weaponTypeId: int
    weaponTypeName: Optional[str]
    acronym: str
    # mapRoleId: int | None


class RoleList(BaseModel):
    roleList: List[Role]


class Box(BaseModel):
    boxName: str
    num: int


class AccountBaseInfo(BaseModel):
    """账户基本信息"""
    name: str  # 名字
    id: int  # 特征码
    creatTime: Optional[int] = None  # 创建时间 ms
    activeDays: Optional[int] = None  # 活跃天数
    level: Optional[int] = None  # 等级
    worldLevel: Optional[int] = None  # 世界等级
    roleNum: Optional[int] = None  # 角色数量
    bigCount: Optional[int] = None  # 大型信标解锁数
    smallCount: Optional[int] = None  # 小型信标解锁数
    achievementCount: Optional[int] = None  # 成就数量
    achievementStar: Optional[int] = None  # 成就星数
    boxList: Optional[List[Optional[Box]]] = None  # 宝箱

    @property
    def is_full(self):
        """完整数据，没有隐藏库街区数据"""
        return isinstance(self.creatTime, int)


class Chain(BaseModel):
    name: Optional[str]
    order: int
    description: Optional[str]
    iconUrl: Optional[str]
    unlocked: bool


class Weapon(BaseModel):
    weaponId: int
    weaponName: str
    weaponType: int
    weaponStarLevel: int
    weaponIcon: Optional[str]
    weaponEffectName: Optional[str]
    effectDescription: Optional[str]


class WeaponData(BaseModel):
    weapon: Weapon
    level: int
    breach: Optional[int]
    resonLevel: Optional[int]


class PhantomProp(BaseModel):
    phantomPropId: int
    name: str
    phantomId: int
    quality: int
    cost: int
    iconUrl: Optional[str]
    skillDescription: Optional[str]


class FetterDetail(BaseModel):
    groupId: int
    name: Optional[str]
    iconUrl: Optional[str]
    num: int
    firstDescription: Optional[str]
    secondDescription: Optional[str]


class Props(BaseModel):
    attributeName: Optional[str]
    iconUrl: Optional[str] = None
    attributeValue: Optional[str]


class EquipPhantom(BaseModel):
    phantomProp: PhantomProp
    cost: int
    quality: int
    level: int
    fetterDetail: FetterDetail
    mainProps: Optional[List[Props]]
    subProps: Optional[List[Props]] = None


class EquipPhantomData(BaseModel):
    cost: int
    equipPhantomList: Union[List[Optional[EquipPhantom]], None, List[None]] = None


class Skill(BaseModel):
    id: int
    type: str
    name: str
    description: str
    iconUrl: str


class SkillData(BaseModel):
    skill: Skill
    level: int


class RoleDetailData(BaseModel):
    role: Role
    level: int
    chainList: List[Chain]
    weaponData: WeaponData
    phantomData: Optional[EquipPhantomData]
    skillList: List[SkillData]

    def get_chain_num(self):
        """获取命座数量"""
        num = 0
        for index, chain in enumerate(self.chainList):
            if chain.unlocked:
                num += 1
        return num

    def get_chain_name(self):
        n = self.get_chain_num()
        return f'{["零", "一", "二", "三", "四", "五", "六"][n]}命'


class CalabashData(BaseModel):
    """数据坞"""
    level: Optional[int]  # 数据坞等级
    baseCatch: Optional[str]  # 基础吸收概率
    strengthenCatch: Optional[str]  # 强化吸收概率
    catchQuality: Optional[int]  # 最高可吸收品质
    cost: Optional[int]  # cost上限
    maxCount: Optional[int]  # 声骸收集进度-max
    unlockCount: Optional[int]  # 声骸收集进度-curr
    isUnlock: bool  # 解锁


class KuroRoleInfo(BaseModel):
    """库洛角色信息"""
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
    """抽卡记录"""
    cardPoolType: str
    resourceId: int
    qualityLevel: int
    resourceType: str
    name: str
    count: int
    time: str

    def __hash__(self):
        return hash((self.resourceId, self.time))


# 定义角色模型
class AbyssRole(BaseModel):
    roleId: int
    iconUrl: Optional[str] = None


# 定义楼层模型
class AbyssFloor(BaseModel):
    floor: int
    picUrl: str
    star: int
    roleList: Optional[List[AbyssRole]] = None


# 定义区域模型
class AbyssArea(BaseModel):
    areaId: int
    areaName: str
    star: int
    maxStar: int
    floorList: Optional[List[AbyssFloor]] = None


# 定义难度模型
class AbyssDifficulty(BaseModel):
    difficulty: int
    difficultyName: str
    towerAreaList: List[AbyssArea]


# 定义顶层模型
class AbyssChallenge(BaseModel):
    isUnlock: bool
    seasonEndTime: Optional[int]
    difficultyList: Optional[List[AbyssDifficulty]]


class ChallengeRole(BaseModel):
    roleName: Optional[str]
    roleHeadIcon: Optional[str]
    roleLevel: Optional[int]
    natureId: Optional[int]
    natureIcon: Optional[Any] = None


class Challenge(BaseModel):
    bossId: Optional[Any] = None
    challengeId: Optional[int] = None
    bossHeadIcon: Optional[str] = None
    bossIconUrl: Optional[str] = None
    bossLevel: Optional[int] = None
    bossName: Optional[str] = None
    passTime: Optional[int] = None
    difficulty: Optional[int] = None
    roles: Optional[List[ChallengeRole]] = None


class ChallengeArea(BaseModel):
    areaId: Optional[Any] = None
    areaName: Optional[Any] = None
    challengeInfo: Optional[Dict[str, List[Challenge]]] = None
    open: bool
    wikiUrl: Optional[Any] = None
    isUnlock: bool


class ExploreItem(BaseModel):
    name: str
    progress: int
    type: int


class AreaInfo(BaseModel):
    areaId: int
    areaName: str
    areaProgress: int
    itemList: List[ExploreItem]


class ExploreCountry(BaseModel):
    countryId: int
    countryName: str
    detailPageFontColor: str
    detailPagePic: str
    detailPageProgressColor: str
    homePageIcon: str


class ExploreArea(BaseModel):
    areaInfoList: Union[List[AreaInfo], None] = None
    country: ExploreCountry
    countryProgress: str


class ExploreList(BaseModel):
    """探索度"""
    exploreList: Union[List[ExploreArea], None] = None
    open: bool
