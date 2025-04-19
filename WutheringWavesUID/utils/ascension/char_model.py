from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from ...utils.util import format_with_defaults


class Stats(BaseModel):
    life: float
    atk: float
    def_: float = Field(..., alias="def")  # `def` is a reserved keyword, use `def_`


class WeaponStats(BaseModel):
    name: str
    value: Union[str, float]
    isRatio: bool
    isPercent: bool


class LevelExp(BaseModel):
    level: int
    exp: int


class SkillLevel(BaseModel):
    name: str
    param: List[List[str]]


class Skill(BaseModel):
    name: str
    desc: str
    param: List[str]
    type: Optional[str] = None
    level: Optional[Dict[int, SkillLevel]] = None

    def get_desc_detail(self):
        return format_with_defaults(self.desc, self.param)


class Chain(BaseModel):
    name: str
    desc: str
    param: List[Union[str, float]]

    def get_desc_detail(self):
        return format_with_defaults(self.desc, self.param)


class AscensionMaterial(BaseModel):
    key: int
    value: int


class CharacterModel(BaseModel):
    name: str
    starLevel: int
    attributeId: int
    weaponTypeId: int
    stats: Dict[str, Dict[str, Stats]]
    skillTree: Dict[int, Dict[str, Skill]]
    chains: Dict[int, Chain]
    ascensions: Dict[str, List[AscensionMaterial]]

    class Config:
        # Updated configuration keys for Pydantic v2
        populate_by_name = True  # Replaces `allow_population_by_field_name`
        str_strip_whitespace = True  # Replaces `anystr_strip_whitespace`
        str_min_length = 1  # Replaces `min_anystr_length`

    def get_max_level_stat(self) -> Stats:
        return self.stats["6"]["90"]


class WeaponModel(BaseModel):
    name: str
    type: int
    starLevel: int
    stats: Dict[str, Dict[str, List[WeaponStats]]]
    effect: str
    effectName: str
    param: List[List[str]]
    desc: str
    ascensions: Dict[str, List[AscensionMaterial]]

    class Config:
        # Updated configuration keys for Pydantic v2
        populate_by_name = True  # Replaces `allow_population_by_field_name`
        str_strip_whitespace = True  # Replaces `anystr_strip_whitespace`
        str_min_length = 1  # Replaces `min_anystr_length`

    def get_max_level_stat_tuple(self) -> List[Tuple[str, str]]:
        stats = self.stats["6"]["90"]
        rets = []
        for stat in stats:
            if stat.isPercent:
                ret = f"{float(stat.value) / 100:.1f}%"
            elif stat.isRatio:
                ret = f"{stat.value * 100:.1f}%"
            else:
                ret = f"{int(stat.value)}"
            rets.append((stat.name, ret))

        return rets

    def get_effect_detail(self):
        return self.effect.format(
            *["(" + "/".join(i) + ")" if len(set(i)) > 1 else i[0] for i in self.param]
        )

    def get_ascensions_max_list(self):
        for i in ["5", "4", "3", "2"]:
            try:
                value = [j.key for j in self.ascensions[i]]
                return value
            except Exception:
                continue
        return []

    def get_weapon_type(self) -> str:
        weapon_type = {
            1: "长刃",
            2: "迅刀",
            3: "佩枪",
            4: "臂铠",
            5: "音感仪",
        }
        return weapon_type.get(self.type, "")
