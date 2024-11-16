from typing import Union, List

from ...utils.damage.damage import DamageAttribute


class WavesRegister(object):
    _id_cls_map = {}

    @classmethod
    def find_class(cls, _id):
        return cls._id_cls_map.get(_id)

    @classmethod
    def register_class(cls, _id, _clz):
        old_cls = cls.find_class(_id)
        if old_cls:
            raise TypeError('%s already register %s for type %s' % (cls, old_cls, _id))
        cls._id_cls_map[_id] = _clz


class WavesWeaponRegister(WavesRegister):
    _id_cls_map = {}


class WavesEchoRegister(WavesRegister):
    _id_cls_map = {}


class WavesCharRegister(WavesRegister):
    _id_cls_map = {}


class DamageDetailRegister(WavesRegister):
    _id_cls_map = {}


class WeaponAbstract(object):
    id = None
    type = None
    name = None

    def __init__(
        self,
        weapon_id: Union[str, int],
        weapon_level: int,
        weapon_breach: Union[int, None] = None,
        weapon_reson_level: Union[int, None] = 1
    ):
        from WutheringWavesUID.utils.ascension.weapon import WavesWeaponResult, get_weapon_detail
        weapon_detail: WavesWeaponResult = get_weapon_detail(weapon_id, weapon_level, weapon_breach, weapon_reson_level)
        self.weapon_id = weapon_id
        self.weapon_level = weapon_level
        self.weapon_breach = weapon_breach
        self.weapon_reson_level = weapon_reson_level
        self.weapon_detail: WavesWeaponResult = weapon_detail

    def do_action(self, func_list: Union[List[str], str], attr: DamageAttribute):
        if isinstance(func_list, str):
            func_list = [func_list]

        for func_name in func_list:
            method = getattr(self, func_name, None)
            if callable(method):
                method(attr)

    def damage(self, attr: DamageAttribute):
        """造成伤害"""
        pass

    def attack_damage(self, attr: DamageAttribute):
        """造成普攻伤害"""
        pass

    def hit_damage(self, attr: DamageAttribute):
        """造成重击伤害"""
        pass

    def skill_damage(self, attr: DamageAttribute):
        """造成共鸣技能伤害"""
        pass

    def liberation_damage(self, attr: DamageAttribute):
        """造成共鸣解放伤害"""
        pass

    def cast_attack(self, attr: DamageAttribute):
        """施放普攻"""
        pass

    def cast_hit(self, attr: DamageAttribute):
        """施放重击"""
        pass

    def cast_skill(self, attr: DamageAttribute):
        """施放共鸣技能"""
        pass

    def cast_liberation(self, attr: DamageAttribute):
        """施放共鸣解放"""
        pass

    def cast_dodge_counter(self, attr: DamageAttribute):
        """施放闪避反击"""
        pass

    def cast_variation(self, attr: DamageAttribute):
        """施放变奏技能"""
        pass

    def skill_create_healing(self, attr: DamageAttribute):
        """共鸣技能造成治疗"""
        pass


class EchoAbstract(object):
    name = None
    id = None

    def do_echo(self, func_list: Union[List[str], str], attr: DamageAttribute):
        if isinstance(func_list, str):
            func_list = [func_list]

        for func_name in func_list:
            method = getattr(self, func_name, None)
            if callable(method):
                method(attr)

    def damage(self, attr: DamageAttribute):
        """造成伤害"""
        pass

    def attack_damage(self, attr: DamageAttribute):
        """造成普攻伤害"""
        self.damage(attr)

    def hit_damage(self, attr: DamageAttribute):
        """造成重击伤害"""
        self.damage(attr)

    def skill_damage(self, attr: DamageAttribute):
        """造成共鸣技能伤害"""
        self.damage(attr)

    def liberation_damage(self, attr: DamageAttribute):
        """造成共鸣解放伤害"""
        self.damage(attr)

    def cast_attack(self, attr: DamageAttribute):
        """施放普攻"""
        self.damage(attr)

    def cast_hit(self, attr: DamageAttribute):
        """施放重击"""
        self.damage(attr)

    def cast_skill(self, attr: DamageAttribute):
        """施放共鸣技能"""
        self.damage(attr)

    def cast_liberation(self, attr: DamageAttribute):
        """施放共鸣解放"""
        self.damage(attr)

    def cast_dodge_counter(self, attr: DamageAttribute):
        """施放闪避反击"""
        self.damage(attr)

    def cast_variation(self, attr: DamageAttribute):
        """施放变奏技能"""
        self.damage(attr)

    def skill_create_healing(self, attr: DamageAttribute):
        """共鸣技能造成治疗"""
        self.damage(attr)
