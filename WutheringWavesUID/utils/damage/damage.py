from typing import Dict, List


class WavesEffect(object):
    def __init__(self, element_msg: str, element_value: any):
        self.element_msg = element_msg
        self.element_value = element_value

    def __str__(self):
        return f"msg={self.element_msg}, value={self.element_value})\n"


def calc_percent_expression(express) -> float:
    """
    计算包含百分比的数学表达式。

    :param express: 字符串形式的数学表达式，例如 "22.38%+13.06%*4"
    :return: 计算结果，浮点数
    """
    # 将百分号替换为小数表示
    express = express.replace('%', '/100')

    try:
        result = eval(express)
    except Exception as e:
        raise ValueError(f"无法计算表达式: {express}") from e

    return result


class PhantomDetail:
    def __init__(self, ph_name: str = '', ph_num: int = 0):
        self.ph_name = ph_name
        self.ph_num = ph_num

    def __str__(self):
        return f"(name={self.ph_name}, count={self.ph_num})"

    @classmethod
    def dict2Object(cls, d):
        res = PhantomDetail()
        res.ph_name = d.get('ph_name', 0)
        res.ph_num = d.get('ph_num', 0)
        return res


class DamageBonusPhantom:
    def __init__(
        self,
        attack_damage=0,
        hit_damage=0,
        skill_damage=0,
        liberation_damage=0,
        heal_bonus=0,
    ):
        """
        初始化 DamageBonusPhantom 类的实例。

        :param attack_damage: 普攻伤害加成
        :param hit_damage: 重击伤害加成
        :param skill_damage: 共鸣技能伤害加成
        :param liberation_damage: 共鸣解放伤害加成
        :param heal_bonus: 治疗效果加成
        """
        self.attack_damage = attack_damage
        self.hit_damage = hit_damage
        self.skill_damage = skill_damage
        self.liberation_damage = liberation_damage
        self.heal_bonus = heal_bonus

    def __str__(self):
        return (
            f"DamageBonusPhantom(\n"
            f"    attack_damage={self.attack_damage}, \n"
            f"    hit_damage={self.hit_damage}, \n"
            f"    skill_damage={self.skill_damage}, \n"
            f"    liberation_damage={self.liberation_damage}, \n"
            f"    heal_bonus={self.heal_bonus}\n"
            f")"
        )

    @classmethod
    def dict2Object(cls, d):
        res = DamageBonusPhantom()
        res.attack_damage = d.get('attack_damage', 0)
        res.hit_damage = d.get('hit_damage', 0)
        res.skill_damage = d.get('skill_damage', 0)
        res.liberation_damage = d.get('liberation_damage', 0)
        res.heal_bonus = d.get('heal_bonus', 0)
        return res


class DamageAttribute:
    def __init__(
        self,
        char_atk=0,
        weapon_atk=0,
        atk_percent=0,
        atk_flat=0,
        skill_multi=0,
        skill_ratio=0,
        dmg_bonus=0,
        dmg_deepen=0,
        crit_rate=0,
        crit_dmg=0,
        character_level=0,
        defense_reduction=0,
        enemy_resistance=0.1,
        dmg_bonus_phantom=None,
        echo_id=0,
    ):
        """
        初始化 DamageAttribute 类的实例。

        :param char_atk: 基础攻击力 (角色基础攻击力
        :param weapon_atk: 基础攻击力 (武器基础攻击力
        :param atk_percent: 攻击力加成百分比 (例如 0.5 表示 50%)
        :param atk_flat: 固定攻击数值加成 (声骸固定攻击)
        :param skill_multi: 技能倍率
        :param skill_ratio: 技能倍率加成 (如命座 椿2命 = 1.2）
        :param dmg_bonus: 伤害加成百分比(热熔伤害加成+技能伤害加成）
        :param dmg_deepen: 伤害加深百分比
        :param crit_rate: 暴击率 (例如 0.5 表示 50%)
        :param crit_dmg: 暴击伤害倍率 (例如 2.0 表示 200%)
        :param character_level: 角色等级
        :param defense_reduction: 减防百分比
        :param enemy_resistance: 敌人抗性百分比
        :param dmg_bonus_phantom: 伤害加成百分比 -> DamageBonusPhantom
        """
        # 角色基础攻击力
        self.char_atk = char_atk
        # 武器基础攻击力
        self.weapon_atk = weapon_atk
        # 攻击力加成百分比
        self.atk_percent = atk_percent
        # 固定攻击数值加成
        self.atk_flat = atk_flat
        # 技能倍率
        self.skill_multi = skill_multi
        # 技能倍率加成 (如命座 椿2命 = 1.2）
        self.skill_ratio = skill_ratio
        # 伤害加成百分比
        self.dmg_bonus = dmg_bonus
        # 伤害加深百分比
        self.dmg_deepen = dmg_deepen
        # 暴击率
        self.crit_rate = crit_rate
        # 暴击伤害
        self.crit_dmg = crit_dmg
        # 角色等级
        self.character_level = character_level
        # 减防百分比
        self.defense_reduction = defense_reduction
        # 敌人抗性百分比
        self.enemy_resistance = enemy_resistance
        # 伤害加成百分比 -> DamageBonusPhantom
        self.dmg_bonus_phantom: DamageBonusPhantom = dmg_bonus_phantom
        # 声骸个数和名字 -> List[PhantomDetail]
        self.ph_detail: List[PhantomDetail] = []
        # 声骸技能id
        self.echo_id = echo_id
        # 效果
        self.effect = []

    def __str__(self):
        ph_details_str = '\n'.join(str(ph) for ph in self.ph_detail)
        return (
            f"\nDamageAttribute(\n"
            f"  char_atk={self.char_atk}, \n"
            f"  weapon_atk={self.weapon_atk}, \n"
            f"  atk_percent={self.atk_percent}, \n"
            f"  atk_flat={self.atk_flat}, \n"
            f"  skill_multi={self.skill_multi}, \n"
            f"  skill_ratio={self.skill_ratio}, \n"
            f"  dmg_bonus={self.dmg_bonus}, \n"
            f"  dmg_deepen={self.dmg_deepen}, \n"
            f"  crit_rate={self.crit_rate}, \n"
            f"  crit_dmg={self.crit_dmg}, \n"
            f"  character_level={self.character_level}, \n"
            f"  defense_reduction={self.defense_reduction}, \n"
            f"  enemy_resistance={self.enemy_resistance}, \n"
            f"  dmg_bonus_phantom={self.dmg_bonus_phantom}, \n"
            f"  ph_detail={ph_details_str}, \n"
            f"  effect={self.effect}\n"
            f")"
        )

    def set_char_atk(self, char_atk: float, msg=''):
        """设置角色基础攻击力"""
        self.char_atk = char_atk
        if msg:
            self.effect.append(WavesEffect(msg, f'{char_atk}'))
        return self

    def set_weapon_atk(self, weapon_atk: float, msg=''):
        """设置武器基础攻击力"""
        self.weapon_atk = weapon_atk
        if msg:
            self.effect.append(WavesEffect(msg, f'{weapon_atk}'))
        return self

    def add_atk_percent(self, atk_percent: float, msg=''):
        """增加攻击力百分比"""
        self.atk_percent += atk_percent
        if msg:
            self.effect.append(WavesEffect(f'{msg}', f'{atk_percent}'))
        return self

    def set_atk_flat(self, atk_flat: float, msg=''):
        """设置固定攻击数值"""
        self.atk_flat = atk_flat
        if msg:
            self.effect.append(WavesEffect(msg, f'{atk_flat}'))
        return self

    def set_skill_multi(self, skill_multi: str, msg=''):
        """设置技能倍率"""
        self.skill_multi = calc_percent_expression(skill_multi)
        if msg:
            self.effect.append(WavesEffect(msg, f'{skill_multi}'))
        return self

    def add_skill_ratio(self, skill_ratio: float, msg=''):
        """设增加技能倍率加成"""
        self.skill_ratio += skill_ratio
        if msg:
            self.effect.append(WavesEffect(msg, f'{skill_ratio}'))
        return self

    def add_dmg_bonus(self, dmg_bonus: float, msg=''):
        """增加伤害加成百分比"""
        self.dmg_bonus += dmg_bonus
        if msg:
            self.effect.append(WavesEffect(msg, f'{dmg_bonus}'))
        return self

    def add_dmg_deepen(self, dmg_deepen: float, msg=''):
        """增加伤害加深百分比"""
        self.dmg_deepen += dmg_deepen
        if msg:
            self.effect.append(WavesEffect(msg, f'{dmg_deepen}'))
        return self

    def add_crit_rate(self, crit_rate: float, msg=''):
        """设置暴击率"""
        self.crit_rate += crit_rate
        if msg:
            self.effect.append(WavesEffect(msg, f'{crit_rate}'))
        return self

    def add_crit_dmg(self, crit_dmg: float, msg=''):
        """设置暴击伤害倍率"""
        self.crit_dmg += crit_dmg
        if msg:
            self.effect.append(WavesEffect(msg, f'{crit_dmg}'))
        return self

    def set_character_level(self, character_level: int, msg=''):
        """设置角色等级"""
        self.character_level = character_level
        if msg:
            self.effect.append(WavesEffect(msg, f'{character_level}'))
        return self

    def add_defense_reduction(self, defense_reduction: float, msg=''):
        """增加减防百分比"""
        self.defense_reduction += defense_reduction
        if msg:
            self.effect.append(WavesEffect(msg, f'{defense_reduction}'))
        return self

    def set_enemy_resistance(self, enemy_resistance: float, msg=''):
        """增加敌人抗性百分比"""
        self.enemy_resistance = enemy_resistance
        if msg:
            self.effect.append(WavesEffect(msg, f'{enemy_resistance}'))
        return self

    def set_dmg_bonus_phantom(self, dmg_bonus_phantom_map: Dict):
        """设置声骸加成"""
        if dmg_bonus_phantom_map:
            dmg_bonus_phantom = DamageBonusPhantom.dict2Object(dmg_bonus_phantom_map)
        else:
            dmg_bonus_phantom = DamageBonusPhantom()
        self.dmg_bonus_phantom = dmg_bonus_phantom
        return self

    def add_ph_detail(self, ph_detail: Dict):
        if not ph_detail:
            return self
        self.ph_detail.append(PhantomDetail.dict2Object(ph_detail))
        return self

    def set_echo_id(self, echo_id: int):
        """声骸技能的id"""
        self.echo_id = echo_id
        return self

    @property
    def base_atk(self):
        """基础攻击力"""
        return self.char_atk + self.weapon_atk

    @property
    def effect_attack(self):
        """
        计算有效攻击力。

        :return: 有效攻击力
        """
        return self.base_atk * (1 + self.atk_percent) + self.atk_flat

    @property
    def defense_ratio(self):
        """
        计算敌人的防御减伤比。

        :return: 防御减伤比
        """
        enemy_defense = 1512
        # 计算公式为 (800 + 8 * 等级) / (800 + 8 * 等级 + 敌人防御 * (1 - 减防))
        return (800 + 8 * self.character_level) / (
            800 + 8 * self.character_level + enemy_defense * (1 - self.defense_reduction))

    def calculate_crit_damage(self):
        """
        计算暴击伤害。

        :return: 暴击伤害值
        """
        # 计算暴击伤害
        return self.effect_attack * self.skill_multi * (1 + self.skill_ratio) * (1 + self.dmg_bonus) * (
            1 + self.dmg_deepen) * (1 - self.enemy_resistance) * self.defense_ratio * self.crit_dmg

    def calculate_expected_damage(self):
        """
        计算期望伤害。

        :return: 期望伤害值
        """
        if self.crit_rate > 1:
            return self.calculate_crit_damage()

        return self.effect_attack * self.skill_multi * (1 + self.skill_ratio) * (1 + self.dmg_bonus) * (
            1 + self.dmg_deepen) * (1 - self.enemy_resistance) * self.defense_ratio * (
            self.crit_rate * (self.crit_dmg - 1) + 1)
