from .damage import DamageAttribute
from .utils import CHAR_ATTR_SIERRA, CHAR_ATTR_SINKING, CHAR_ATTR_MOLTEN, CHAR_ATTR_VOID, liberation_damage, \
    attack_damage, hit_damage, skill_damage, CHAR_ATTR_CELESTIAL, CHAR_ATTR_FREEZING, temp_atk
from ...utils.damage.abstract import EchoAbstract, WavesEchoRegister


class Echo_390070051(EchoAbstract):
    id = 390070051
    name = "先锋幼岩"


class Echo_390070052(EchoAbstract):
    id = 390070052
    name = "裂变幼岩"


class Echo_390070053(EchoAbstract):
    id = 390070053
    name = "惊蛰猎手"


class Echo_390070064(EchoAbstract):
    id = 390070064
    name = "鸣泣战士"


class Echo_390070065(EchoAbstract):
    id = 390070065
    name = "审判战士"


class Echo_390070066(EchoAbstract):
    id = 390070066
    name = "咔嚓嚓"


class Echo_390070067(EchoAbstract):
    id = 390070067
    name = "阿嗞嗞"


class Echo_390070068(EchoAbstract):
    id = 390070068
    name = "呼咻咻"


class Echo_390070069(EchoAbstract):
    id = 390070069
    name = "呜咔咔"


class Echo_390070070(EchoAbstract):
    id = 390070070
    name = "破霜猎手"


class Echo_390070071(EchoAbstract):
    id = 390070071
    name = "巡徊猎手"


class Echo_390070074(EchoAbstract):
    id = 390070074
    name = "游弋蝶"


class Echo_390070075(EchoAbstract):
    id = 390070075
    name = "碎獠猪"


class Echo_390070076(EchoAbstract):
    id = 390070076
    name = "咕咕河豚"


class Echo_390070077(EchoAbstract):
    id = 390070077
    name = "遁地鼠"


class Echo_390070078(EchoAbstract):
    id = 390070078
    name = "绿熔蜥（稚形）"


class Echo_390070079(EchoAbstract):
    id = 390070079
    name = "刺玫菇（稚形）"


class Echo_390070100(EchoAbstract):
    id = 390070100
    name = "火鬃狼"


class Echo_390070105(EchoAbstract):
    id = 390070105
    name = "寒霜陆龟"


class Echo_390077004(EchoAbstract):
    id = 390077004
    name = "紫羽鹭"


class Echo_390077005(EchoAbstract):
    id = 390077005
    name = "青羽鹭"


class Echo_390077012(EchoAbstract):
    id = 390077012
    name = "热熔棱镜"


class Echo_390077013(EchoAbstract):
    id = 390077013
    name = "冷凝棱镜"


class Echo_390077016(EchoAbstract):
    id = 390077016
    name = "衍射棱镜"


class Echo_390077017(EchoAbstract):
    id = 390077017
    name = "湮灭棱镜"


class Echo_390077021(EchoAbstract):
    id = 390077021
    name = "坚岩斗士"


class Echo_390077022(EchoAbstract):
    id = 390077022
    name = "奏谕乐师"


class Echo_390077023(EchoAbstract):
    id = 390077023
    name = "振铎乐师"


class Echo_390077024(EchoAbstract):
    id = 390077024
    name = "磐石守卫"


class Echo_390077025(EchoAbstract):
    id = 390077025
    name = "冥渊守卫"


class Echo_390077028(EchoAbstract):
    id = 390077028
    name = "绿熔蜥"


class Echo_390077029(EchoAbstract):
    id = 390077029
    name = "刺玫菇"


class Echo_390077033(EchoAbstract):
    id = 390077033
    name = "暗鬃狼"


class Echo_390077038(EchoAbstract):
    id = 390077038
    name = "箭簇熊"


class Echo_390080003(EchoAbstract):
    id = 390080003
    name = "云闪之鳞"

    # 终结一击命中后，自身导电伤害加成提升12.00%，共鸣解放伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_VOID:
            title = self.name
            msg = '自身导电伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == liberation_damage:
            title = self.name
            msg = '共鸣解放伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_390080005(EchoAbstract):
    id = 390080005
    name = "鸣钟之龟"


class Echo_390080007(EchoAbstract):
    id = 390080007
    name = "燎照之骑"

    # 最后一段命中敌人后，自身热熔伤害加成提升12.00%，普攻伤害加成提升12.00%，持续15秒。

    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_MOLTEN:
            title = self.name
            msg = '自身热熔伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == attack_damage:
            title = self.name
            msg = '普攻伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_390180010(EchoAbstract):
    id = 390180010
    name = "异相·飞廉之猩"


class Echo_391070105(EchoAbstract):
    id = 391070105
    name = "异相·寒霜陆龟"


class Echo_391077024(EchoAbstract):
    id = 391077024
    name = "异相·磐石守卫"


class Echo_391080003(Echo_390080003):
    id = 391080003
    name = "异相·云闪之鳞"


class Echo_6000038(EchoAbstract):
    id = 6000038
    name = "幼猿"


class Echo_6000039(EchoAbstract):
    id = 6000039
    name = "朔雷之鳞"

    # 爪击命中后，自身导电伤害加成提升12.00%，重击伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_VOID:
            title = self.name
            msg = '自身导电伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == hit_damage:
            title = self.name
            msg = '重击伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000040(EchoAbstract):
    id = 6000040
    name = "戏猿"


class Echo_6000041(EchoAbstract):
    id = 6000041
    name = "晶螯蝎"


class Echo_6000042(EchoAbstract):
    id = 6000042
    name = "无冠者"

    # 幻形后，自身湮灭伤害加成提升12.00%，共鸣技能伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_SINKING:
            title = self.name
            msg = '自身湮灭伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == skill_damage:
            title = self.name
            msg = '共鸣技能伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000043(EchoAbstract):
    id = 6000043
    name = "飞廉之猩"

    # 追击命中后，自身气动伤害加成提升12.00%，重击伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_SIERRA:
            title = self.name
            msg = '气动伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == hit_damage:
            title = self.name
            msg = '重击伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000044(EchoAbstract):
    id = 6000044
    name = "辉萤军势"

    # 每次冲击使自身冷凝伤害加成提升4.00%，共鸣技能伤害加成提升4.00%，最多3层
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_FREEZING:
            title = self.name
            msg = '冷凝伤害加成提升4.00%*3'
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == skill_damage:
            title = self.name
            msg = '共鸣技能伤害加成提升4.00%*3'
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000045(EchoAbstract):
    id = 6000045
    name = "哀声鸷"

    # 自身衍射伤害加成提升12.00%，共鸣解放伤害加成提升12.00%
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_CELESTIAL:
            title = self.name
            msg = '衍射伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == liberation_damage:
            title = self.name
            msg = '共鸣解放伤害加成提升12.00%'
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000046(EchoAbstract):
    id = 6000046
    name = "车刃镰"


class Echo_6000047(EchoAbstract):
    id = 6000047
    name = "啾啾河豚"


class Echo_6000048(EchoAbstract):
    id = 6000048
    name = "聚械机偶"

    # 施放声骸技能后，自身攻击提升12.00%
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_template == temp_atk:
            title = self.name
            msg = '自身攻击提升12.00%'
            attr.add_atk_percent(0.12, title, msg)


class Echo_6000049(EchoAbstract):
    id = 6000049
    name = "巡哨机傀"


class Echo_6000050(EchoAbstract):
    id = 6000050
    name = "通行灯偶"


class Echo_6000051(EchoAbstract):
    id = 6000051
    name = "叮咚咚"


class Echo_6000052(EchoAbstract):
    id = 6000052
    name = "无常凶鹭"


class Echo_6000053(EchoAbstract):
    id = 6000053
    name = "无妄者"


class Echo_6000054(EchoAbstract):
    id = 6000054
    name = "融火虫"


class Echo_6000055(EchoAbstract):
    id = 6000055
    name = "侏侏鸵"


class Echo_6000056(EchoAbstract):
    id = 6000056
    name = "雪鬃狼"


class Echo_6000057(EchoAbstract):
    id = 6000057
    name = "游鳞机枢"


class Echo_6000058(EchoAbstract):
    id = 6000058
    name = "踏光兽"


class Echo_6000059(EchoAbstract):
    id = 6000059
    name = "角"

    # 自身的共鸣技能伤害加成提升16.00%
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_damage == skill_damage:
            title = self.name
            msg = '共鸣技能伤害加成提升16.00%'
            attr.add_dmg_bonus(0.16, title, msg)


class Echo_6000060(EchoAbstract):
    id = 6000060
    name = "无归的谬误"

    # 自身共鸣效率提升10%，全队角色攻击提升10%
    # def damage(self, attr: DamageAttribute, isGroup: bool = False):
    #     title = self.name
    #     msg = '全队角色攻击提升10%'
    #     attr.add_atk_percent(0.1, title, msg)


class Echo_6000145(Echo_6000045):
    id = 6000145
    name = "异相·哀声鸷"


class Echo_6010052(EchoAbstract):
    id = 6010052
    name = "异相·无常凶鹭"


def register_echo():
    WavesEchoRegister.register_class(Echo_390070051.id, Echo_390070051)
    WavesEchoRegister.register_class(Echo_390070052.id, Echo_390070052)
    WavesEchoRegister.register_class(Echo_390070053.id, Echo_390070053)
    WavesEchoRegister.register_class(Echo_390070064.id, Echo_390070064)
    WavesEchoRegister.register_class(Echo_390070065.id, Echo_390070065)
    WavesEchoRegister.register_class(Echo_390070066.id, Echo_390070066)
    WavesEchoRegister.register_class(Echo_390070067.id, Echo_390070067)
    WavesEchoRegister.register_class(Echo_390070068.id, Echo_390070068)
    WavesEchoRegister.register_class(Echo_390070069.id, Echo_390070069)
    WavesEchoRegister.register_class(Echo_390070070.id, Echo_390070070)
    WavesEchoRegister.register_class(Echo_390070071.id, Echo_390070071)
    WavesEchoRegister.register_class(Echo_390070074.id, Echo_390070074)
    WavesEchoRegister.register_class(Echo_390070075.id, Echo_390070075)
    WavesEchoRegister.register_class(Echo_390070076.id, Echo_390070076)
    WavesEchoRegister.register_class(Echo_390070077.id, Echo_390070077)
    WavesEchoRegister.register_class(Echo_390070078.id, Echo_390070078)
    WavesEchoRegister.register_class(Echo_390070079.id, Echo_390070079)
    WavesEchoRegister.register_class(Echo_390070100.id, Echo_390070100)
    WavesEchoRegister.register_class(Echo_390070105.id, Echo_390070105)
    WavesEchoRegister.register_class(Echo_390077004.id, Echo_390077004)
    WavesEchoRegister.register_class(Echo_390077005.id, Echo_390077005)
    WavesEchoRegister.register_class(Echo_390077012.id, Echo_390077012)
    WavesEchoRegister.register_class(Echo_390077013.id, Echo_390077013)
    WavesEchoRegister.register_class(Echo_390077016.id, Echo_390077016)
    WavesEchoRegister.register_class(Echo_390077017.id, Echo_390077017)
    WavesEchoRegister.register_class(Echo_390077021.id, Echo_390077021)
    WavesEchoRegister.register_class(Echo_390077022.id, Echo_390077022)
    WavesEchoRegister.register_class(Echo_390077023.id, Echo_390077023)
    WavesEchoRegister.register_class(Echo_390077024.id, Echo_390077024)
    WavesEchoRegister.register_class(Echo_390077025.id, Echo_390077025)
    WavesEchoRegister.register_class(Echo_390077028.id, Echo_390077028)
    WavesEchoRegister.register_class(Echo_390077029.id, Echo_390077029)
    WavesEchoRegister.register_class(Echo_390077033.id, Echo_390077033)
    WavesEchoRegister.register_class(Echo_390077038.id, Echo_390077038)
    WavesEchoRegister.register_class(Echo_390080003.id, Echo_390080003)
    WavesEchoRegister.register_class(Echo_390080005.id, Echo_390080005)
    WavesEchoRegister.register_class(Echo_390080007.id, Echo_390080007)
    WavesEchoRegister.register_class(Echo_390180010.id, Echo_390180010)
    WavesEchoRegister.register_class(Echo_391070105.id, Echo_391070105)
    WavesEchoRegister.register_class(Echo_391077024.id, Echo_391077024)
    WavesEchoRegister.register_class(Echo_391080003.id, Echo_391080003)
    WavesEchoRegister.register_class(Echo_6000038.id, Echo_6000038)
    WavesEchoRegister.register_class(Echo_6000039.id, Echo_6000039)
    WavesEchoRegister.register_class(Echo_6000040.id, Echo_6000040)
    WavesEchoRegister.register_class(Echo_6000041.id, Echo_6000041)
    WavesEchoRegister.register_class(Echo_6000042.id, Echo_6000042)
    WavesEchoRegister.register_class(Echo_6000043.id, Echo_6000043)
    WavesEchoRegister.register_class(Echo_6000044.id, Echo_6000044)
    WavesEchoRegister.register_class(Echo_6000045.id, Echo_6000045)
    WavesEchoRegister.register_class(Echo_6000046.id, Echo_6000046)
    WavesEchoRegister.register_class(Echo_6000047.id, Echo_6000047)
    WavesEchoRegister.register_class(Echo_6000048.id, Echo_6000048)
    WavesEchoRegister.register_class(Echo_6000049.id, Echo_6000049)
    WavesEchoRegister.register_class(Echo_6000050.id, Echo_6000050)
    WavesEchoRegister.register_class(Echo_6000051.id, Echo_6000051)
    WavesEchoRegister.register_class(Echo_6000052.id, Echo_6000052)
    WavesEchoRegister.register_class(Echo_6000053.id, Echo_6000053)
    WavesEchoRegister.register_class(Echo_6000054.id, Echo_6000054)
    WavesEchoRegister.register_class(Echo_6000055.id, Echo_6000055)
    WavesEchoRegister.register_class(Echo_6000056.id, Echo_6000056)
    WavesEchoRegister.register_class(Echo_6000057.id, Echo_6000057)
    WavesEchoRegister.register_class(Echo_6000058.id, Echo_6000058)
    WavesEchoRegister.register_class(Echo_6000059.id, Echo_6000059)
    WavesEchoRegister.register_class(Echo_6000060.id, Echo_6000060)
    WavesEchoRegister.register_class(Echo_6000145.id, Echo_6000145)
    WavesEchoRegister.register_class(Echo_6010052.id, Echo_6010052)
