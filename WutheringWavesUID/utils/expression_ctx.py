from typing import Dict, Optional

from pydantic import BaseModel

from .calc import WuWaCalc
from ..utils.api.model import RoleDetailData
from .damage.abstract import DamageRankRegister
from .damage.utils import comma_separated_number
from .char_info_utils import get_all_role_detail_info
from .calculate import get_calc_map, calc_phantom_score, get_total_score_bg


class WavesCharRank(BaseModel):
    roleId: int  # 角色id
    roleName: str  # 角色名字
    starLevel: int  # 角色星级
    level: int  # 角色等级
    chain: int  # 命座
    chainName: str  # 命座
    score: float  # 角色评分
    score_bg: str  # 评分背景
    expected_damage: Optional[float]  # 期望伤害


async def get_waves_char_rank(uid, all_role_detail, need_expected_damage=False):
    if not all_role_detail:
        all_role_detail = await get_all_role_detail_info(uid)
    if isinstance(all_role_detail, Dict):
        temp = all_role_detail.values()
    else:
        temp = all_role_detail if all_role_detail else []
    waves_char_rank = []
    for role_detail in temp:
        if not isinstance(role_detail, RoleDetailData):
            role_detail = RoleDetailData(**role_detail)

        phantom_score = 0
        calc: WuWaCalc = WuWaCalc(role_detail)
        # calc_temp = None
        expected_damage = None

        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            equipPhantomList = role_detail.phantomData.equipPhantomList

            calc.phantom_pre = calc.prepare_phantom()
            calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
            calc.calc_temp = get_calc_map(calc.phantom_card, role_detail.role.roleName)
            for i, _phantom in enumerate(equipPhantomList):
                if _phantom and _phantom.phantomProp:
                    props = _phantom.get_props()
                    _score, _bg = calc_phantom_score(
                        role_detail.role.roleName, props, _phantom.cost, calc.calc_temp
                    )
                    phantom_score += _score

            if need_expected_damage:
                rankDetail = DamageRankRegister.find_class(str(role_detail.role.roleId))
                if rankDetail:
                    calc.role_card = calc.enhance_summation_card_value(
                        calc.phantom_card
                    )
                    calc.damageAttribute = calc.card_sort_map_to_attribute(
                        calc.role_card
                    )
                    _, expected_damage = rankDetail["func"](
                        calc.damageAttribute, role_detail
                    )
                    expected_damage = comma_separated_number(expected_damage)

        wcr = WavesCharRank(
            **{
                "roleId": role_detail.role.roleId,
                "roleName": role_detail.role.roleName,
                "starLevel": role_detail.role.starLevel,
                "level": role_detail.level,
                "chain": role_detail.get_chain_num(),
                "chainName": role_detail.get_chain_name(),
                "score": phantom_score,
                "score_bg": get_total_score_bg(
                    role_detail.role.roleName, phantom_score, calc.calc_temp
                ),
                "expected_damage": expected_damage,
            }
        )
        waves_char_rank.append(wcr)

    return waves_char_rank
