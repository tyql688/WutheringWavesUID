import re
from typing import List

from gsuid_core.logger import logger
from ..utils.api.model import RoleDetailData
from ..utils.ascension.sonata import WavesSonataResult, get_sonata_detail
from ..utils.ascension.weapon import WavesWeaponResult, get_weapon_detail
from ..utils.name_convert import (
    alias_to_sonata_name,
    alias_to_weapon_name,
    weapon_name_to_weapon_id,
)
from ..utils.resource.constant import SONATA_FIRST_ID

phantom_main_value = [
    {"name": "攻击", "values": ["18%", "30%", "33%"]},
    {"name": "生命", "values": ["22.8%", "30%", "33%"]},
    {"name": "防御", "values": ["18%", "38%", "41.8%"]},
    {"name": "暴击", "values": ["0%", "0%", "22%"]},
    {"name": "暴击伤害", "values": ["0%", "0%", "44%"]},
    {"name": "共鸣效率", "values": ["0%", "32%", "0%"]},
    {"name": "属性伤害加成", "values": ["0%", "30%", "0%"]},
    {"name": "治疗效果加成", "values": ["0%", "0%", "26.4%"]},
]
phantom_main_value_map = {i["name"]: i["values"] for i in phantom_main_value}


class ReplaceRole:
    PREFIX_RE: list[str] = ["角色", "人物", "面板", "信息", "个人信息"]

    def __init__(self):
        self.roleId: str | None = None  # 角色id
        self.roleName: str | None = None  # 角色名字
        self.level: str | None = None  # 等级
        self.chain: str | None = None  # 共鸣链
        self.skill: list[int] | None = None  # 技能


class ReplaceWeapon:
    PREFIX_RE: list[str] = ["武器", "装备"]

    def __init__(self):
        self.weaponId: str | None = None  # 武器id
        self.weaponName: str | None = None  # 武器名字
        self.level: str | None = None  # 等级
        self.resonLevel: str | None = None  # 精炼


class ReplaceSonata:
    PREFIX_RE: list[str] = ["合鸣", "套装"]

    def __init__(self):
        self.sonataName: str | None = None  # 套装名字


class ReplacePhantom:
    PREFIX_RE: list[str] = ["声骸", "圣遗物"]

    # 主词条更换

    def __init__(self):
        self.mainc4: List[str] | None = None  # 主词条更换
        self.mainc3: List[str] | None = None  # 主词条更换
        self.mainc1: List[str] | None = None  # 主词条更换


class ReplaceResult:
    def __init__(self):
        self.role: ReplaceRole = ReplaceRole()
        self.weapon: ReplaceWeapon = ReplaceWeapon()
        self.sonata: ReplaceSonata = ReplaceSonata()
        self.phantom: ReplacePhantom = ReplacePhantom()


def parse_chain(content: str) -> tuple[str, str] | None:
    pattern = r"(?:(命|命座|共鸣链|链)[0-6零一二三四五六满]|[0-6零一二三四五六满](命|命座|共鸣链|链))"
    match = re.search(pattern, content)
    if match:
        matched_string = match.group(0)
        number = re.search(r"[0-6零一二三四五六满]", matched_string)
        if number:
            number = number.group(0)
            number_map = {
                "零": "0",
                "一": "1",
                "二": "2",
                "三": "3",
                "四": "4",
                "五": "5",
                "六": "6",
                "满": "6",
            }
            return matched_string, number_map.get(number, number)
    return None


def parse_weapon_reson_level(content: str) -> tuple[str, str] | None:
    pattern = r"(?:(精炼|谐振|精|谐|振)[1-5一二三四五满]|[1-5一二三四五满](精炼|谐振|精|谐|振))"
    match = re.search(pattern, content)
    if match:
        matched_string = match.group(0)
        number = re.search(r"[1-5一二三四五满]", matched_string)
        if number:
            number = number.group(0)
            number_map = {
                "一": "1",
                "二": "2",
                "三": "3",
                "四": "4",
                "五": "5",
                "满": "5",
            }
            return matched_string, number_map.get(number, number)
    return None


def parse_level(content: str) -> tuple[str, str] | None:
    pattern = r"(?:(等级|级)([1-9][0-9]?)|([1-9][0-9]?)(等级|级))"
    match = re.search(pattern, content)
    if match:
        matched_string = match.group(0)
        level = match.group(2) or match.group(3)
        return matched_string, level
    return None


def parse_skills(content: str) -> list[int] | None:
    pattern = r"(技能等级|天赋|技能)\s*((?:\d{1,2}\s*){1,5})"
    match = re.search(pattern, content)
    if match:
        skills_str = match.group(2)
        skills = [int(skill) for skill in skills_str.split() if 1 <= int(skill) <= 10]
    else:
        return None

    while len(skills) < 5:
        skills.append(10)

    return skills[:5]


def parse_sonatas(content: str) -> str | None:
    pattern = r"([^\d]+)"
    match = re.search(pattern, content)

    if match:
        type1 = match.group(1).strip()
        return type1

    return None


def parse_main(content: str) -> list[tuple[str, list[str], str]]:
    results = []
    c4_attrs = []
    c3_attrs = []
    c1_attrs = []

    attr_map = {
        "暴击": "暴击",
        "爆伤": "暴击伤害",
        "暴伤": "暴击伤害",
        "攻击": "攻击",
        "攻": "攻击",
        "属性": "属性伤害加成",
        "属": "属性伤害加成",
        "生命": "生命",
        "防御": "防御",
        "暴": "暴击",
        "爆": "暴击伤害",
        "防": "防御",
        "生": "生命",
    }

    content = re.sub(r"^(?:主词条|主词|主|main)\s*", "", content)

    # 处理带位置的属性
    position_pattern = r"[cC]([134])\s*([^\s]+)"
    for match in re.finditer(position_pattern, content):
        position = match.group(1)
        attrs_str = match.group(2)

        # 解析属性组合
        attr_pattern = r"([1-9])?\s*([^\s1-9]+)"
        for attr_match in re.finditer(attr_pattern, attrs_str):
            count = int(attr_match.group(1) or 1)
            attr = attr_match.group(2)

            base_attr = None
            for key, value in attr_map.items():
                if key in attr:
                    base_attr = value
                    break

            if base_attr:
                attr_list = [base_attr] * count
                if position == "4":
                    c4_attrs.extend(attr_list)
                elif position == "3":
                    c3_attrs.extend(attr_list)
                elif position == "1":
                    c1_attrs.extend(attr_list)

    # 添加结果
    if c4_attrs:
        results.append((f"c4{''.join(c4_attrs)}", c4_attrs, "4"))
    if c3_attrs:
        results.append((f"c3{''.join(c3_attrs)}", c3_attrs, "3"))
    if c1_attrs:
        results.append((f"c1{''.join(c3_attrs)}", c1_attrs, "1"))

    return results


def get_breach(level: int):
    if level <= 20:
        breach = 0
    elif level <= 40:
        breach = 1
    elif level <= 50:
        breach = 2
    elif level <= 60:
        breach = 3
    elif level <= 70:
        breach = 4
    elif level <= 80:
        breach = 5
    elif level <= 90:
        breach = 6
    else:
        breach = 0
    return breach


class ChangeParser:

    def __init__(self, content: str):
        self.rr: ReplaceResult = ReplaceResult()
        self.matched_segments: list[str] = []
        contents = content.split("换")
        for cont in contents:
            cont = cont.strip(" ")
            self.process_content(cont)

    def process_content(self, cont: str):
        matched_list = []
        for prefix in self.rr.role.PREFIX_RE:
            if cont.startswith(prefix):
                cont = cont[len(prefix) :].strip()
                matched_list.extend(self.parse_role(cont))
                break
        for prefix in self.rr.weapon.PREFIX_RE:
            if cont.startswith(prefix):
                cont = cont[len(prefix) :].strip()
                matched_list.extend(self.parse_weapon(cont))
                break
        for prefix in self.rr.phantom.PREFIX_RE:
            if cont.startswith(prefix):
                cont = cont[len(prefix) :].strip()
                matched_list.extend(self.parse_phantom(cont))
                break
        for prefix in self.rr.sonata.PREFIX_RE:
            if cont.startswith(prefix):
                cont = cont[len(prefix) :].strip()
                matched_list.extend(self.parse_sonata(cont))
                break

        if matched_list:
            self.matched_segments.append(" ".join(matched_list))

    def parse_role(self, cont: str) -> list[str]:
        matched_list = [f"换{self.rr.role.PREFIX_RE[0]}"]
        level = parse_level(cont)
        if level:
            matched_string, level_value = level
            self.rr.role.level = level_value
            cont = cont.replace(matched_string, "")
            matched_list.append(matched_string)
        constellation = parse_chain(cont)
        if constellation:
            matched_string, const_value = constellation
            self.rr.role.chain = const_value
            cont = cont.replace(matched_string, "")
            matched_list.append(matched_string)
        skills = parse_skills(cont)
        if skills:
            self.rr.role.skill = skills
            matched_list.append(f"技能等级 {' '.join(map(str, skills))}")
        return matched_list

    def parse_weapon(self, cont: str) -> list[str]:
        matched_list = [f"换{self.rr.weapon.PREFIX_RE[0]}"]
        weapon_level = parse_level(cont)
        if weapon_level:
            matched_string, level_value = weapon_level
            self.rr.weapon.level = level_value
            cont = cont.replace(matched_string, "")
            matched_list.append(matched_string)
        reson_level = parse_weapon_reson_level(cont)
        if reson_level:
            matched_string, reson_value = reson_level
            self.rr.weapon.resonLevel = reson_value
            cont = cont.replace(matched_string, "")
            matched_list.append(matched_string)

        cont = cont.strip()
        if cont:
            weaponName = alias_to_weapon_name(cont)
            weaponId = weapon_name_to_weapon_id(weaponName)
            if weaponName and weaponId:
                self.rr.weapon.weaponName = weaponName
                self.rr.weapon.weaponId = weaponId
                matched_list.append(cont)
        return matched_list

    def parse_sonata(self, cont: str) -> list[str]:
        matched_list = []
        sonata_name = parse_sonatas(cont)
        sonata_name = alias_to_sonata_name(sonata_name)
        if sonata_name:
            self.rr.sonata.sonataName = sonata_name
            matched_list.append(f"换{self.rr.sonata.PREFIX_RE[0]} {sonata_name}")
        return matched_list

    def parse_phantom(self, cont: str) -> list[str]:
        matched_list = [f"换{self.rr.phantom.PREFIX_RE[0]}"]
        main_results = parse_main(cont)
        for main_result in main_results:
            matched_string, attr_list, position = main_result
            if position == "1":
                self.rr.phantom.mainc1 = attr_list
            elif position == "3":
                self.rr.phantom.mainc3 = attr_list
            else:  # position == "4" or default
                self.rr.phantom.mainc4 = attr_list
            matched_list.append(matched_string)
        return matched_list

    def get_matched_content(self) -> str:
        return ";".join(self.matched_segments)


async def change_role_detail(
    role_detail: RoleDetailData, change_list_regex: str
) -> tuple[RoleDetailData, str]:
    parser: ChangeParser = ChangeParser(change_list_regex)
    parserResult: ReplaceResult = parser.rr
    if parserResult.role.skill:
        skill_list = role_detail.get_skill_list()
        for i, level in zip(skill_list[:5], parserResult.role.skill):
            for j in role_detail.skillList:
                if j.skill.type != i.skill.type:
                    continue
                j.level = int(level)

    if parserResult.role.level:
        roleLevel = int(parserResult.role.level)
        role_detail.role.level = roleLevel
        role_detail.level = roleLevel
        role_detail.role.breach = get_breach(roleLevel)

    if parserResult.role.chain:
        chain = int(parserResult.role.chain)
        if chain == 0:
            for temp in role_detail.chainList:
                temp.unlocked = False

        for chainNum, temp in enumerate(role_detail.chainList, start=1):
            print(temp)
            print(type(temp))
            if chainNum <= chain:
                temp.unlocked = True
            else:
                temp.unlocked = False

    # 武器
    if parserResult.weapon.weaponId:
        weapon_detail: WavesWeaponResult | None = get_weapon_detail(
            parserResult.weapon.weaponId, 90
        )
        if weapon_detail:
            weapon = role_detail.weaponData.weapon
            if weapon.weaponType == weapon_detail.type:
                weapon.weaponId = int(parserResult.weapon.weaponId)
                weapon.weaponName = weapon_detail.name
                weapon.weaponStarLevel = weapon_detail.starLevel

    if parserResult.weapon.level:
        weaponLevel = int(parserResult.weapon.level)
        role_detail.weaponData.level = weaponLevel
        role_detail.weaponData.breach = get_breach(weaponLevel)

    if parserResult.weapon.resonLevel:
        role_detail.weaponData.resonLevel = int(parserResult.weapon.resonLevel)

    if parserResult.sonata.sonataName:
        sonata_result: WavesSonataResult | None = get_sonata_detail(
            parserResult.sonata.sonataName
        )
        if (
            sonata_result
            and role_detail.phantomData
            and role_detail.phantomData.equipPhantomList
        ):
            for index, ep in enumerate(role_detail.phantomData.equipPhantomList):
                if not ep:
                    continue
                ep.fetterDetail.name = sonata_result.name
                if index == 0 and ep.phantomProp.phantomId not in SONATA_FIRST_ID.get(
                    sonata_result.name, []
                ):
                    ep.phantomProp.phantomId = SONATA_FIRST_ID.get(
                        sonata_result.name, []
                    )[0]

    logger.debug(
        f"声骸主词条: c4-{parserResult.phantom.mainc4}， c3-{parserResult.phantom.mainc3}, c1-{parserResult.phantom.mainc1}"
    )
    if parserResult.phantom.mainc4:
        index = 0
        mainc = parserResult.phantom.mainc4
        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            for ep in role_detail.phantomData.equipPhantomList:
                if ep.cost != 4:
                    continue
                props = ep.mainProps
                if not props:
                    continue
                if index >= len(mainc):
                    break
                props[0].attributeName = mainc[index]
                props[0].attributeValue = phantom_main_value_map[mainc[index]][2]
                index += 1
    if parserResult.phantom.mainc3:
        index = 0
        mainc = parserResult.phantom.mainc3
        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            for ep in role_detail.phantomData.equipPhantomList:
                if ep.cost != 3:
                    continue
                props = ep.mainProps
                if not props:
                    continue
                if index >= len(mainc):
                    break
                if mainc[index] == "属性伤害加成":
                    shuxing = f"{role_detail.role.attributeName}伤害加成"
                else:
                    shuxing = f"攻击"
                props[0].attributeName = shuxing
                props[0].attributeValue = phantom_main_value_map[mainc[index]][1]
                index += 1

    if parserResult.phantom.mainc1:
        index = 0
        mainc = parserResult.phantom.mainc1
        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            for ep in role_detail.phantomData.equipPhantomList:
                if ep.cost != 1:
                    continue
                props = ep.mainProps
                if not props:
                    continue
                if index >= len(mainc):
                    break
                props[0].attributeName = mainc[index]
                props[0].attributeValue = phantom_main_value_map[mainc[index]][0]
                index += 1

    return role_detail, parser.get_matched_content()


def test_change_parser():
    test_cases = [
        "换武器90级5精炼 换角色技能等级 10 10 10 10 16命等级100 技能等级 10 10 10 10 1",
        "换武器5谐振90级 换角色技能等级 8 9 1 1 1满命等级9级 ",
        "换武器折枝专武精炼5 换角色三命等级80 技能等级 7 7 7 7 7",
        "换角色6命 换武器折枝专武 技能等级 6 5 4 3 2",
        "换武器90级 换角色命座6 换人物等级90 技能等级 3 2 1",
        "换角色等级50 换角色2命",
        "换武器80级3精炼",
        "换角色等级70 换武器90级 换角色4命",
        "换武器 换角色",
        "换武器90级 换角色命座6 换人物等级90 额外信息",
        # 新增测试用例
        "换声骸主词条4暴击暴伤",
        "换声骸mainc3双攻击",
        "换声骸主c1属性",
        "换合鸣寒冰套装",
        "换套装寒冰",
        "换角色90级6命 换武器90级5精炼 换声骸主词条4暴击 换合鸣寒冰",
        "换声骸主词条4双属性 换合鸣寒冰 换角色90级",
        "换声骸主词条1双攻击 换声骸主词条3暴击 换声骸主词条4暴伤",
    ]

    for _, test_case in enumerate(test_cases):
        parser = ChangeParser(test_case)
        matched_content = parser.get_matched_content()
        print(f"Matched Content: {matched_content}")


# test_change_parser()
