from typing import Dict, List, Union, Optional

from pydantic import Field, BaseModel


class Stats(BaseModel):
    life: float
    atk: float
    def_: float = Field(..., alias="def")  # `def` is a reserved keyword, use `def_`


class LevelExp(BaseModel):
    level: int
    exp: int


class SkillLevel(BaseModel):
    name: str
    param: List[List[Union[str, int]]]


class Skill(BaseModel):
    name: str
    desc: str
    param: List[str]
    type: Optional[str] = None
    level: Optional[Dict[int, SkillLevel]] = None

    def get_desc_detail(self):
        return self.desc.format(*self.param)


class Chain(BaseModel):
    name: str
    desc: str
    param: List[Union[str, float]]

    def get_desc_detail(self):
        return self.desc.format(*self.param)


class CharacterModel(BaseModel):
    name: str
    starLevel: int
    stats: Dict[str, Dict[str, Stats]]
    levelExp: List[int]
    skillTree: Dict[int, Dict[str, Skill]]
    chains: Dict[int, Chain]

    class Config:
        # Updated configuration keys for Pydantic v2
        populate_by_name = True  # Replaces `allow_population_by_field_name`
        str_strip_whitespace = True  # Replaces `anystr_strip_whitespace`
        str_min_length = 1  # Replaces `min_anystr_length`

    def get_max_level_stat(self) -> Stats:
        return self.stats["6"]["90"]
