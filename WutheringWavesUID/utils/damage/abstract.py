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


class DamageRankRegister(WavesRegister):
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
        from ...utils.ascension.weapon import WavesWeaponResult, get_weapon_detail
        weapon_detail: WavesWeaponResult = get_weapon_detail(weapon_id, weapon_level, weapon_breach, weapon_reson_level)
        self.weapon_id = weapon_id
        self.weapon_level = weapon_level
        self.weapon_breach = weapon_breach
        self.weapon_reson_level = weapon_reson_level
        self.weapon_detail: WavesWeaponResult = weapon_detail

    def do_action(self, func_list: Union[List[str], str], attr: DamageAttribute, isGroup: bool = False):
        if isinstance(func_list, str):
            func_list = [func_list]

        for func_name in func_list:
            method = getattr(self, func_name, None)
            if callable(method):
                if method(attr, isGroup):
                    return

    def get_title(self):
        return f"{self.name}-{self.weapon_detail.get_resonLevel_name()}"

    def param(self, param):
        return self.weapon_detail.param[param][self.weapon_reson_level - 1]

    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        """造成伤害"""
        pass

    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """施放普攻"""
        pass

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """施放重击"""
        pass

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        pass

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        pass

    def cast_dodge_counter(self, attr: DamageAttribute, isGroup: bool = False):
        """施放闪避反击"""
        pass

    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        pass

    def skill_create_healing(self, attr: DamageAttribute, isGroup: bool = False):
        """共鸣技能造成治疗"""
        pass


class EchoAbstract(object):
    name = None
    id = None

    def do_echo(self, attr: DamageAttribute, isGroup: bool = False):
        self.damage(attr, isGroup)

    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        """造成伤害"""
        pass


class CharAbstract(object):
    name = None
    id = None
    starLevel = None

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        """
        获得buff

        :param attr: 人物伤害属性
        :param chain: 命座
        :param resonLevel: 武器谐振
        :param isGroup: 是否组队

        """
        pass
