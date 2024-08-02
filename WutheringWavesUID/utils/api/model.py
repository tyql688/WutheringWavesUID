from typing import TypedDict, Dict, List


class EnergyData(TypedDict):
    """结晶波片"""
    name: str
    refreshTimeStamp: str
    cur: int
    total: int


class LivenessData(TypedDict):
    """活跃度"""
    name: str
    img: str
    cur: int
    total: int


class BattlePassData(TypedDict):
    """电台等级"""
    name: str
    cur: int
    total: int


class WavesDailyData(TypedDict):
    """每日数据"""
    gameId: int
    userId: int
    serverId: str
    roleId: str
    roleName: str
    energyData: Dict[str, EnergyData]
    livenessData: Dict[str, LivenessData]
    battlePassData: List[BattlePassData]
