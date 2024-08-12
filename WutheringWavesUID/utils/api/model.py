from typing import List, Union, Optional

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
    breach: int
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
    """账户基本信息"""
    name: str  # 名字
    id: int  # 特征码
    creatTime: Optional[int]  # 创建时间 ms
    activeDays: Optional[int]  # 活跃天数
    level: Optional[int]  # 等级
    worldLevel: Optional[int]  # 世界等级
    roleNum: Optional[int]  # 角色数量
    bigCount: Optional[int]  # 大型信标解锁数
    smallCount: Optional[int]  # 小型信标解锁数
    achievementCount: Optional[int]  # 成就数量
    achievementStar: Optional[int]  # 成就星数
    boxList: Optional[list[Optional[Box]]]  # 宝箱


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


class WeaponData(BaseModel):
    weapon: Weapon
    level: int
    breach: int
    # resonLevel: int


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


class Props(BaseModel):
    attributeName: str
    iconUrl: Union[str, None] = None
    attributeValue: str


class EquipPhantom(BaseModel):
    phantomProp: PhantomProp
    cost: int
    quality: int
    level: int
    fetterDetail: FetterDetail
    mainProps: List[Props]
    subProps: Union[List[Props], None] = None


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
    phantomData: Union[EquipPhantomData, None] = None
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
    level: int  # 数据坞等级
    baseCatch: str  # 基础吸收概率
    strengthenCatch: str  # 强化吸收概率
    catchQuality: int  # 最高可吸收品质
    cost: int  # cost上限
    maxCount: int  # 声骸收集进度-max
    unlockCount: int  # 声骸收集进度-curr
    isUnlock: bool  # 解锁


class ExploreData(BaseModel):
    """探索度"""
    countryCode: int  # 城市code: 1
    countryName: str  # 城市名字: 瑝珑
    countryProgress: str  # 进度: 75.81


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
