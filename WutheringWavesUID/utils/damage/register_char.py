from .damage import DamageAttribute
from .utils import CHAR_ATTR_CELESTIAL, CHAR_ATTR_FREEZING, attack_damage, skill_damage, hit_damage, CHAR_ATTR_MOLTEN, \
    liberation_damage
from ...utils.damage.abstract import CharAbstract, WavesCharRegister, WavesWeaponRegister


class Char_1102(CharAbstract):
    id = 1102
    name = "散华"
    starLevel = 4

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        """获得buff"""
        if chain >= 6:
            title = "散华-六命"
            msg = "队伍中的角色攻击提升20%"
            attr.add_atk_percent(0.2, title, msg)

        title = "散华-合鸣效果-轻云出月"
        msg = "下一个登场的共鸣者攻击提升22.5%"
        attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = "散华-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if attack_damage == attr.char_damage:
            title = "散华-延奏技能"
            msg = "下一位登场角色普攻伤害加深38%"
            attr.add_dmg_deepen(0.38, title, msg)


class Char_1103(CharAbstract):
    id = 1103
    name = "白芷"
    starLevel = 4


class Char_1104(CharAbstract):
    id = 1104
    name = "凌阳"
    starLevel = 5


class Char_1105(CharAbstract):
    id = 1105
    name = "折枝"
    starLevel = 5

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        if chain >= 4:
            title = f"{self.name}-四命"
            msg = "折枝施放共鸣解放虚实境趣时，队伍中角色攻击提升20%"
            attr.add_atk_percent(0.2, title, msg)

        title = f"{self.name}-合鸣效果-轻云出月"
        msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
        attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = f"{self.name}-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_attr == CHAR_ATTR_FREEZING:
            title = f"{self.name}-延奏技能"
            msg = "下一位登场角色冷凝伤害加深20%"
            attr.add_dmg_bonus(0.2, title, msg)

        if skill_damage == attr.char_damage:
            title = f"{self.name}-延奏技能"
            msg = "下一位登场角色共鸣技能伤害加深25%"
            attr.add_dmg_deepen(0.25, title, msg)


class Char_1106(CharAbstract):
    id = 1106
    name = "釉瑚"
    starLevel = 4


class Char_1202(CharAbstract):
    id = 1202
    name = "炽霞"
    starLevel = 4


class Char_1203(CharAbstract):
    id = 1203
    name = "安可"
    starLevel = 5


class Char_1204(CharAbstract):
    id = 1204
    name = "莫特斐"
    starLevel = 4

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        """获得buff"""
        if chain >= 6:
            title = "莫特斐-六命"
            msg = "施放共鸣解放暴烈终曲时，队伍中的角色攻击提升20%"
            attr.add_atk_percent(0.2, title, msg)

        title = "莫特斐-合鸣效果-轻云出月"
        msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
        attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = "莫特斐-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if hit_damage == attr.char_damage:
            title = "莫特斐-延奏技能"
            msg = "下一位登场角色重击伤害加深38%"
            attr.add_dmg_deepen(0.38, title, msg)

        # 停驻之烟
        weapon_id = 21030015
        weapon_clz = WavesWeaponRegister.find_class(weapon_id)
        if weapon_clz:
            w = weapon_clz(weapon_id,
                           90,
                           6,
                           resonLevel)
            w.do_action('damage', attr, isGroup)


class Char_1205(CharAbstract):
    id = 1205
    name = "长离"
    starLevel = 5

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        """获得buff"""
        if chain >= 4:
            title = "长离-四命"
            msg = "施放变奏技能后，队伍中的角色攻击提升20%"
            attr.add_atk_percent(0.2, title, msg)

        if attr.char_attr == CHAR_ATTR_MOLTEN:
            title = "长离-延奏技能"
            msg = "下一位登场角色热熔伤害加深20%"
            attr.add_dmg_deepen(0.2, title, msg)

        if liberation_damage == attr.char_damage:
            title = "长离-延奏技能"
            msg = "下一位登场角色共鸣解放伤害加深25%"
            attr.add_dmg_deepen(0.25, title, msg)


class Char_1301(CharAbstract):
    id = 1301
    name = "卡卡罗"
    starLevel = 5


class Char_1302(CharAbstract):
    id = 1302
    name = "吟霖"
    starLevel = 5


class Char_1303(CharAbstract):
    id = 1303
    name = "渊武"
    starLevel = 4


class Char_1304(CharAbstract):
    id = 1304
    name = "今汐"
    starLevel = 5


class Char_1305(CharAbstract):
    id = 1305
    name = "相里要"
    starLevel = 5


class Char_1402(CharAbstract):
    id = 1402
    name = "秧秧"
    starLevel = 4


class Char_1403(CharAbstract):
    id = 1403
    name = "秋水"
    starLevel = 4


class Char_1404(CharAbstract):
    id = 1404
    name = "忌炎"
    starLevel = 5


class Char_1405(CharAbstract):
    id = 1405
    name = "鉴心"
    starLevel = 5


class Char_1501(CharAbstract):
    id = 1501
    name = "漂泊者·衍射"
    starLevel = 5


class Char_1502(CharAbstract):
    id = 1502
    name = "漂泊者·衍射"
    starLevel = 5


class Char_1503(CharAbstract):
    id = 1503
    name = "维里奈"
    starLevel = 5

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        """获得buff"""
        title = "维里奈-固有技能-自然的献礼"
        msg = "队伍中的角色攻击提升20%"
        attr.add_atk_percent(0.2, title, msg)

        if chain >= 4 and attr.char_attr == CHAR_ATTR_CELESTIAL:
            title = "维里奈-四命"
            msg = "队伍中的角色衍射伤害加成提升15%"
            attr.add_dmg_bonus(0.4, title, msg)

        title = "维里奈-合鸣效果-隐世回光"
        msg = "全队共鸣者攻击提升15%"
        attr.add_atk_percent(0.15, title, msg)

        title = "维里奈-声骸技能-鸣钟之龟"
        msg = "全队角色10.00%的伤害提升"
        attr.add_dmg_bonus(0.1, title, msg)

        title = "维里奈-延奏技能"
        msg = "队伍中的角色全伤害加深15%"
        attr.add_dmg_deepen(0.15, title, msg)


class Char_1504(CharAbstract):
    id = 1504
    name = "灯灯"
    starLevel = 4

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        if chain >= 6:
            title = f"{self.name}-六命"
            msg = "施放共鸣解放时，队伍中的角色的攻击提升20%"
            attr.add_atk_percent(0.2, title, msg)

        title = f"{self.name}-合鸣效果-轻云出月"
        msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
        attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = f"{self.name}-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if skill_damage == attr.char_damage:
            title = f"{self.name}-延奏技能"
            msg = "下一位登场角色共鸣技能伤害加深38%"
            attr.add_dmg_deepen(0.38, title, msg)


class Char_1505(CharAbstract):
    id = 1505
    name = "守岸人"
    starLevel = 5

    def do_buff(self, attr: DamageAttribute, chain: int = 0, resonLevel: int = 1, isGroup: bool = True):
        """获得buff"""
        if chain >= 2:
            title = "守岸人-二命"
            msg = "队伍中的角色攻击提升40%"
            attr.add_atk_percent(0.4, title, msg)

        title = "守岸人-合鸣效果-隐世回光"
        msg = "全队共鸣者攻击提升15%"
        attr.add_atk_percent(0.15, title, msg)

        # 星序协响
        weapon_clz = WavesWeaponRegister.find_class(21050036)
        if weapon_clz:
            w = weapon_clz(21050036,
                           90,
                           6,
                           resonLevel)
            w.do_action('skill_create_healing', attr, isGroup)

        title = "守岸人-声骸技能-无归的谬误"
        msg = "全队角色攻击提升10%"
        attr.add_atk_percent(0.1, title, msg)

        title = "守岸人-共鸣解放"
        msg = "暴击提升12.5%+暴击伤害提升25%"
        attr.add_crit_rate(0.125)
        attr.add_crit_dmg(0.25)
        attr.add_effect(title, msg)

        title = "守岸人-延奏技能"
        msg = "队伍中的角色全伤害加深15%"
        attr.add_dmg_deepen(0.15, title, msg)


class Char_1601(CharAbstract):
    id = 1601
    name = "桃祈"
    starLevel = 4


class Char_1602(CharAbstract):
    id = 1602
    name = "丹瑾"
    starLevel = 4


class Char_1603(CharAbstract):
    id = 1603
    name = "椿"
    starLevel = 5


class Char_1604(CharAbstract):
    id = 1604
    name = "漂泊者·湮灭"
    starLevel = 5


class Char_1605(CharAbstract):
    id = 1605
    name = "漂泊者·湮灭"
    starLevel = 5


def register_char():
    WavesCharRegister.register_class(Char_1102.id, Char_1102)
    WavesCharRegister.register_class(Char_1103.id, Char_1103)
    WavesCharRegister.register_class(Char_1104.id, Char_1104)
    WavesCharRegister.register_class(Char_1105.id, Char_1105)
    WavesCharRegister.register_class(Char_1106.id, Char_1106)
    WavesCharRegister.register_class(Char_1202.id, Char_1202)
    WavesCharRegister.register_class(Char_1203.id, Char_1203)
    WavesCharRegister.register_class(Char_1204.id, Char_1204)
    WavesCharRegister.register_class(Char_1205.id, Char_1205)
    WavesCharRegister.register_class(Char_1301.id, Char_1301)
    WavesCharRegister.register_class(Char_1302.id, Char_1302)
    WavesCharRegister.register_class(Char_1303.id, Char_1303)
    WavesCharRegister.register_class(Char_1304.id, Char_1304)
    WavesCharRegister.register_class(Char_1305.id, Char_1305)
    WavesCharRegister.register_class(Char_1402.id, Char_1402)
    WavesCharRegister.register_class(Char_1403.id, Char_1403)
    WavesCharRegister.register_class(Char_1404.id, Char_1404)
    WavesCharRegister.register_class(Char_1405.id, Char_1405)
    WavesCharRegister.register_class(Char_1501.id, Char_1501)
    WavesCharRegister.register_class(Char_1502.id, Char_1502)
    WavesCharRegister.register_class(Char_1503.id, Char_1503)
    WavesCharRegister.register_class(Char_1504.id, Char_1504)
    WavesCharRegister.register_class(Char_1505.id, Char_1505)
    WavesCharRegister.register_class(Char_1601.id, Char_1601)
    WavesCharRegister.register_class(Char_1602.id, Char_1602)
    WavesCharRegister.register_class(Char_1603.id, Char_1603)
    WavesCharRegister.register_class(Char_1604.id, Char_1604)
    WavesCharRegister.register_class(Char_1605.id, Char_1605)
