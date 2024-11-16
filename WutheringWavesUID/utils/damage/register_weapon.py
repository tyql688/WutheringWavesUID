from .damage import DamageAttribute, calc_percent_expression
from ..damage.abstract import WeaponAbstract, WavesWeaponRegister


class Weapon_21010011(WeaponAbstract):
    id = 21010011
    type = 1
    name = "教学长刃"


class Weapon_21010012(WeaponAbstract):
    id = 21010012
    type = 1
    name = "原初长刃·朴石"


class Weapon_21010013(WeaponAbstract):
    id = 21010013
    type = 1
    name = "暗夜长刃·玄明"


class Weapon_21010015(WeaponAbstract):
    id = 21010015
    type = 1
    name = "浩境粼光"


class Weapon_21010016(WeaponAbstract):
    id = 21010016
    type = 1
    name = "苍鳞千嶂"


class Weapon_21010023(WeaponAbstract):
    id = 21010023
    type = 1
    name = "源能长刃·测壹"


class Weapon_21010024(WeaponAbstract):
    id = 21010024
    type = 1
    name = "异响空灵"


class Weapon_21010026(WeaponAbstract):
    id = 21010026
    type = 1
    name = "时和岁稔"


class Weapon_21010034(WeaponAbstract):
    id = 21010034
    type = 1
    name = "重破刃-41型"


class Weapon_21010043(WeaponAbstract):
    id = 21010043
    type = 1
    name = "远行者长刃·辟路"


class Weapon_21010044(WeaponAbstract):
    id = 21010044
    type = 1
    name = "永夜长明"


class Weapon_21010053(WeaponAbstract):
    id = 21010053
    type = 1
    name = "戍关长刃·定军"


class Weapon_21010063(WeaponAbstract):
    id = 21010063
    type = 1
    name = "钧天正音"


class Weapon_21010064(WeaponAbstract):
    id = 21010064
    type = 1
    name = "东落"


class Weapon_21010073(WeaponAbstract):
    id = 21010073
    type = 1
    name = ""


class Weapon_21010074(WeaponAbstract):
    id = 21010074
    type = 1
    name = "纹秋"


class Weapon_21010084(WeaponAbstract):
    id = 21010084
    type = 1
    name = "凋亡频移"


class Weapon_21020011(WeaponAbstract):
    id = 21020011
    type = 2
    name = "教学迅刀"


class Weapon_21020012(WeaponAbstract):
    id = 21020012
    type = 2
    name = "原初迅刀·鸣雨"


class Weapon_21020013(WeaponAbstract):
    id = 21020013
    type = 2
    name = "暗夜迅刀·黑闪"


class Weapon_21020015(WeaponAbstract):
    id = 21020015
    type = 2
    name = "千古洑流"

    def damage(self, attr: DamageAttribute):
        """造成伤害"""
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*{self.weapon_detail.param[2][self.weapon_reson_level - 1]}"
        attr.add_atk_percent(calc_percent_expression(dmg))

    def skill_damage(self, attr: DamageAttribute):
        """造成共鸣技能伤害"""
        self.damage(attr)

    def liberation_damage(self, attr: DamageAttribute):
        """造成共鸣解放伤害"""
        self.damage(attr)


class Weapon_21020016(WeaponAbstract):
    id = 21020016
    type = 2
    name = "赫奕流明"

    def damage(self, attr: DamageAttribute):
        """造成伤害"""
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*14"
        attr.add_dmg_bonus(calc_percent_expression(dmg))

    def skill_damage(self, attr: DamageAttribute):
        """造成共鸣技能伤害"""
        self.damage(attr)


class Weapon_21020017(WeaponAbstract):
    id = 21020017
    type = 2
    name = "心之锚"

    def damage(self, attr: DamageAttribute):
        """造成伤害"""
        dmg = f"{self.weapon_detail.param[3][self.weapon_reson_level - 1]}*{self.weapon_detail.param[5][self.weapon_reson_level - 1]}"
        attr.add_atk_percent(calc_percent_expression(dmg))

        dmg = f"{self.weapon_detail.param[6][self.weapon_reson_level - 5]}*{self.weapon_detail.param[7][self.weapon_reson_level - 1]}"
        attr.add_crit_rate(calc_percent_expression(dmg))

    def attack_damage(self, attr: DamageAttribute):
        """造成普攻伤害"""
        self.damage(attr)

    def skill_damage(self, attr: DamageAttribute):
        """造成共鸣技能伤害"""
        self.damage(attr)

    def liberation_damage(self, attr: DamageAttribute):
        """造成共鸣解放伤害"""
        self.damage(attr)


class Weapon_21020023(WeaponAbstract):
    id = 21020023
    type = 2
    name = "源能迅刀·测贰"


class Weapon_21020024(WeaponAbstract):
    id = 21020024
    type = 2
    name = "行进序曲"


class Weapon_21020026(WeaponAbstract):
    id = 21020026
    type = 2
    name = "裁春"

    def attack_damage(self, attr: DamageAttribute):
        """造成普攻伤害"""
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*{self.weapon_detail.param[3][self.weapon_reson_level - 1]}+{self.weapon_detail.param[4][self.weapon_reson_level - 1]}"
        attr.add_dmg_bonus(calc_percent_expression(dmg))


class Weapon_21020034(WeaponAbstract):
    id = 21020034
    type = 2
    name = "瞬斩刀-18型"


class Weapon_21020043(WeaponAbstract):
    id = 21020043
    type = 2
    name = "远行者迅刀·旅迹"


class Weapon_21020044(WeaponAbstract):
    id = 21020044
    type = 2
    name = "不归孤军"


class Weapon_21020053(WeaponAbstract):
    id = 21020053
    type = 2
    name = "戍关迅刀·镇海"


class Weapon_21020063(WeaponAbstract):
    id = 21020063
    type = 2
    name = ""


class Weapon_21020064(WeaponAbstract):
    id = 21020064
    type = 2
    name = "西升"


class Weapon_21020074(WeaponAbstract):
    id = 21020074
    type = 2
    name = "飞景"


class Weapon_21020084(WeaponAbstract):
    id = 21020084
    type = 2
    name = "永续坍缩"


class Weapon_21030011(WeaponAbstract):
    id = 21030011
    type = 3
    name = "教学佩枪"


class Weapon_21030012(WeaponAbstract):
    id = 21030012
    type = 3
    name = "原初佩枪·穿林"


class Weapon_21030013(WeaponAbstract):
    id = 21030013
    type = 3
    name = "暗夜佩枪·暗星"


class Weapon_21030015(WeaponAbstract):
    id = 21030015
    type = 3
    name = "停驻之烟"


class Weapon_21030023(WeaponAbstract):
    id = 21030023
    type = 3
    name = "源能佩枪·测叁"


class Weapon_21030024(WeaponAbstract):
    id = 21030024
    type = 3
    name = "华彩乐段"


class Weapon_21030034(WeaponAbstract):
    id = 21030034
    type = 3
    name = "穿击枪-26型"


class Weapon_21030043(WeaponAbstract):
    id = 21030043
    type = 3
    name = "远行者佩枪·洞察"


class Weapon_21030044(WeaponAbstract):
    id = 21030044
    type = 3
    name = "无眠烈火"


class Weapon_21030053(WeaponAbstract):
    id = 21030053
    type = 3
    name = "戍关佩枪·平云"


class Weapon_21030063(WeaponAbstract):
    id = 21030063
    type = 3
    name = ""


class Weapon_21030064(WeaponAbstract):
    id = 21030064
    type = 3
    name = "飞逝"


class Weapon_21030074(WeaponAbstract):
    id = 21030074
    type = 3
    name = "奔雷"


class Weapon_21030084(WeaponAbstract):
    id = 21030084
    type = 3
    name = "悖论喷流"


class Weapon_21040011(WeaponAbstract):
    id = 21040011
    type = 4
    name = "教学臂铠"


class Weapon_21040012(WeaponAbstract):
    id = 21040012
    type = 4
    name = "原初臂铠·磐岩"


class Weapon_21040013(WeaponAbstract):
    id = 21040013
    type = 4
    name = "暗夜臂铠·夜芒"


class Weapon_21040015(WeaponAbstract):
    id = 21040015
    type = 4
    name = "擎渊怒涛"


class Weapon_21040016(WeaponAbstract):
    id = 21040016
    type = 4
    name = "诸方玄枢"


class Weapon_21040023(WeaponAbstract):
    id = 21040023
    type = 4
    name = "源能臂铠·测肆"


class Weapon_21040024(WeaponAbstract):
    id = 21040024
    type = 4
    name = "呼啸重音"


class Weapon_21040034(WeaponAbstract):
    id = 21040034
    type = 4
    name = "钢影拳-21丁型"


class Weapon_21040043(WeaponAbstract):
    id = 21040043
    type = 4
    name = "远行者臂铠·破障"


class Weapon_21040044(WeaponAbstract):
    id = 21040044
    type = 4
    name = "袍泽之固"


class Weapon_21040053(WeaponAbstract):
    id = 21040053
    type = 4
    name = "戍关臂铠·拔山"


class Weapon_21040063(WeaponAbstract):
    id = 21040063
    type = 4
    name = "戍关臂铠·拔山"


class Weapon_21040064(WeaponAbstract):
    id = 21040064
    type = 4
    name = "骇行"


class Weapon_21040074(WeaponAbstract):
    id = 21040074
    type = 4
    name = "金掌"


class Weapon_21040084(WeaponAbstract):
    id = 21040084
    type = 4
    name = "尘云旋臂"


class Weapon_21050011(WeaponAbstract):
    id = 21050011
    type = 5
    name = "教学音感仪"


class Weapon_21050012(WeaponAbstract):
    id = 21050012
    type = 5
    name = "原初音感仪·听浪"


class Weapon_21050013(WeaponAbstract):
    id = 21050013
    type = 5
    name = "暗夜矩阵·暝光"


class Weapon_21050015(WeaponAbstract):
    id = 21050015
    type = 5
    name = "漪澜浮录"


class Weapon_21050016(WeaponAbstract):
    id = 21050016
    type = 5
    name = "掣傀之手"


class Weapon_21050023(WeaponAbstract):
    id = 21050023
    type = 5
    name = "源能音感仪·测五"


class Weapon_21050024(WeaponAbstract):
    id = 21050024
    type = 5
    name = "奇幻变奏"


class Weapon_21050026(WeaponAbstract):
    id = 21050026
    type = 5
    name = "琼枝冰绡"


class Weapon_21050034(WeaponAbstract):
    id = 21050034
    type = 5
    name = "鸣动仪-25型"


class Weapon_21050036(WeaponAbstract):
    id = 21050036
    type = 5
    name = "星序协响"


class Weapon_21050043(WeaponAbstract):
    id = 21050043
    type = 5
    name = "远行者矩阵·探幽"


class Weapon_21050044(WeaponAbstract):
    id = 21050044
    type = 5
    name = "今州守望"


class Weapon_21050053(WeaponAbstract):
    id = 21050053
    type = 5
    name = "戍关音感仪·留光"


class Weapon_21050063(WeaponAbstract):
    id = 21050063
    type = 5
    name = "戍关音感仪·留光"


class Weapon_21050064(WeaponAbstract):
    id = 21050064
    type = 5
    name = "异度"


class Weapon_21050074(WeaponAbstract):
    id = 21050074
    type = 5
    name = "清音"


class Weapon_21050084(WeaponAbstract):
    id = 21050084
    type = 5
    name = "核熔星盘"


def register_weapon():
    WavesWeaponRegister.register_class(Weapon_21010011.id, Weapon_21010011)
    WavesWeaponRegister.register_class(Weapon_21010012.id, Weapon_21010012)
    WavesWeaponRegister.register_class(Weapon_21010013.id, Weapon_21010013)
    WavesWeaponRegister.register_class(Weapon_21010015.id, Weapon_21010015)
    WavesWeaponRegister.register_class(Weapon_21010016.id, Weapon_21010016)
    WavesWeaponRegister.register_class(Weapon_21010023.id, Weapon_21010023)
    WavesWeaponRegister.register_class(Weapon_21010024.id, Weapon_21010024)
    WavesWeaponRegister.register_class(Weapon_21010026.id, Weapon_21010026)
    WavesWeaponRegister.register_class(Weapon_21010034.id, Weapon_21010034)
    WavesWeaponRegister.register_class(Weapon_21010043.id, Weapon_21010043)
    WavesWeaponRegister.register_class(Weapon_21010044.id, Weapon_21010044)
    WavesWeaponRegister.register_class(Weapon_21010053.id, Weapon_21010053)
    WavesWeaponRegister.register_class(Weapon_21010063.id, Weapon_21010063)
    WavesWeaponRegister.register_class(Weapon_21010064.id, Weapon_21010064)
    WavesWeaponRegister.register_class(Weapon_21010073.id, Weapon_21010073)
    WavesWeaponRegister.register_class(Weapon_21010074.id, Weapon_21010074)
    WavesWeaponRegister.register_class(Weapon_21010084.id, Weapon_21010084)
    WavesWeaponRegister.register_class(Weapon_21020011.id, Weapon_21020011)
    WavesWeaponRegister.register_class(Weapon_21020012.id, Weapon_21020012)
    WavesWeaponRegister.register_class(Weapon_21020013.id, Weapon_21020013)
    WavesWeaponRegister.register_class(Weapon_21020015.id, Weapon_21020015)
    WavesWeaponRegister.register_class(Weapon_21020016.id, Weapon_21020016)
    WavesWeaponRegister.register_class(Weapon_21020017.id, Weapon_21020017)
    WavesWeaponRegister.register_class(Weapon_21020023.id, Weapon_21020023)
    WavesWeaponRegister.register_class(Weapon_21020024.id, Weapon_21020024)
    WavesWeaponRegister.register_class(Weapon_21020026.id, Weapon_21020026)
    WavesWeaponRegister.register_class(Weapon_21020034.id, Weapon_21020034)
    WavesWeaponRegister.register_class(Weapon_21020043.id, Weapon_21020043)
    WavesWeaponRegister.register_class(Weapon_21020044.id, Weapon_21020044)
    WavesWeaponRegister.register_class(Weapon_21020053.id, Weapon_21020053)
    WavesWeaponRegister.register_class(Weapon_21020063.id, Weapon_21020063)
    WavesWeaponRegister.register_class(Weapon_21020064.id, Weapon_21020064)
    WavesWeaponRegister.register_class(Weapon_21020074.id, Weapon_21020074)
    WavesWeaponRegister.register_class(Weapon_21020084.id, Weapon_21020084)
    WavesWeaponRegister.register_class(Weapon_21030011.id, Weapon_21030011)
    WavesWeaponRegister.register_class(Weapon_21030012.id, Weapon_21030012)
    WavesWeaponRegister.register_class(Weapon_21030013.id, Weapon_21030013)
    WavesWeaponRegister.register_class(Weapon_21030015.id, Weapon_21030015)
    WavesWeaponRegister.register_class(Weapon_21030023.id, Weapon_21030023)
    WavesWeaponRegister.register_class(Weapon_21030024.id, Weapon_21030024)
    WavesWeaponRegister.register_class(Weapon_21030034.id, Weapon_21030034)
    WavesWeaponRegister.register_class(Weapon_21030043.id, Weapon_21030043)
    WavesWeaponRegister.register_class(Weapon_21030044.id, Weapon_21030044)
    WavesWeaponRegister.register_class(Weapon_21030053.id, Weapon_21030053)
    WavesWeaponRegister.register_class(Weapon_21030063.id, Weapon_21030063)
    WavesWeaponRegister.register_class(Weapon_21030064.id, Weapon_21030064)
    WavesWeaponRegister.register_class(Weapon_21030074.id, Weapon_21030074)
    WavesWeaponRegister.register_class(Weapon_21030084.id, Weapon_21030084)
    WavesWeaponRegister.register_class(Weapon_21040011.id, Weapon_21040011)
    WavesWeaponRegister.register_class(Weapon_21040012.id, Weapon_21040012)
    WavesWeaponRegister.register_class(Weapon_21040013.id, Weapon_21040013)
    WavesWeaponRegister.register_class(Weapon_21040015.id, Weapon_21040015)
    WavesWeaponRegister.register_class(Weapon_21040016.id, Weapon_21040016)
    WavesWeaponRegister.register_class(Weapon_21040023.id, Weapon_21040023)
    WavesWeaponRegister.register_class(Weapon_21040024.id, Weapon_21040024)
    WavesWeaponRegister.register_class(Weapon_21040034.id, Weapon_21040034)
    WavesWeaponRegister.register_class(Weapon_21040043.id, Weapon_21040043)
    WavesWeaponRegister.register_class(Weapon_21040044.id, Weapon_21040044)
    WavesWeaponRegister.register_class(Weapon_21040053.id, Weapon_21040053)
    WavesWeaponRegister.register_class(Weapon_21040063.id, Weapon_21040063)
    WavesWeaponRegister.register_class(Weapon_21040064.id, Weapon_21040064)
    WavesWeaponRegister.register_class(Weapon_21040074.id, Weapon_21040074)
    WavesWeaponRegister.register_class(Weapon_21040084.id, Weapon_21040084)
    WavesWeaponRegister.register_class(Weapon_21050011.id, Weapon_21050011)
    WavesWeaponRegister.register_class(Weapon_21050012.id, Weapon_21050012)
    WavesWeaponRegister.register_class(Weapon_21050013.id, Weapon_21050013)
    WavesWeaponRegister.register_class(Weapon_21050015.id, Weapon_21050015)
    WavesWeaponRegister.register_class(Weapon_21050016.id, Weapon_21050016)
    WavesWeaponRegister.register_class(Weapon_21050023.id, Weapon_21050023)
    WavesWeaponRegister.register_class(Weapon_21050024.id, Weapon_21050024)
    WavesWeaponRegister.register_class(Weapon_21050026.id, Weapon_21050026)
    WavesWeaponRegister.register_class(Weapon_21050034.id, Weapon_21050034)
    WavesWeaponRegister.register_class(Weapon_21050036.id, Weapon_21050036)
    WavesWeaponRegister.register_class(Weapon_21050043.id, Weapon_21050043)
    WavesWeaponRegister.register_class(Weapon_21050044.id, Weapon_21050044)
    WavesWeaponRegister.register_class(Weapon_21050053.id, Weapon_21050053)
    WavesWeaponRegister.register_class(Weapon_21050063.id, Weapon_21050063)
    WavesWeaponRegister.register_class(Weapon_21050064.id, Weapon_21050064)
    WavesWeaponRegister.register_class(Weapon_21050074.id, Weapon_21050074)
    WavesWeaponRegister.register_class(Weapon_21050084.id, Weapon_21050084)