from ....utils.damage.abstract import DamageDetailRegister, DamageRankRegister


def register_damage():
    from .damage_1102 import damage_detail as damage_1102
    from .damage_1203 import damage_detail as damage_1203
    from .damage_1205 import damage_detail as damage_1205
    from .damage_1302 import damage_detail as damage_1302
    from .damage_1304 import damage_detail as damage_1304
    from .damage_1305 import damage_detail as damage_1305
    from .damage_1404 import damage_detail as damage_1404
    from .damage_1505 import damage_detail as damage_1505
    from .damage_1602 import damage_detail as damage_1602
    from .damage_1603 import damage_detail as damage_1603
    from .damage_1604 import damage_detail as damage_1604

    # 散华
    DamageDetailRegister.register_class("1102", damage_1102)

    # 安可
    DamageDetailRegister.register_class("1203", damage_1203)
    # 长离
    DamageDetailRegister.register_class("1205", damage_1205)

    # 吟霖
    DamageDetailRegister.register_class("1302", damage_1302)
    # 今汐
    DamageDetailRegister.register_class("1304", damage_1304)
    # 相里要
    DamageDetailRegister.register_class("1305", damage_1305)

    # 忌炎
    DamageDetailRegister.register_class("1404", damage_1404)

    # 守岸人
    DamageDetailRegister.register_class("1505", damage_1505)

    # 丹瑾
    DamageDetailRegister.register_class("1602", damage_1602)
    # 椿
    DamageDetailRegister.register_class("1603", damage_1603)
    # 暗主女
    DamageDetailRegister.register_class("1604", damage_1604)
    # 暗主男
    DamageDetailRegister.register_class("1605", damage_1604)


def register_rank():
    from .damage_1102 import rank as rank_1102
    from .damage_1203 import rank as rank_1203
    from .damage_1205 import rank as rank_1205
    from .damage_1302 import rank as rank_1302
    from .damage_1304 import rank as rank_1304
    from .damage_1305 import rank as rank_1305
    from .damage_1404 import rank as rank_1404
    from .damage_1505 import rank as rank_1505
    from .damage_1602 import rank as rank_1602
    from .damage_1603 import rank as rank_1603
    from .damage_1604 import rank as rank_1604

    # 长离
    DamageRankRegister.register_class("1102", rank_1102)

    # 安可
    DamageRankRegister.register_class("1203", rank_1203)
    # 长离
    DamageRankRegister.register_class("1205", rank_1205)

    # 吟霖
    DamageRankRegister.register_class("1302", rank_1302)
    # 今汐
    DamageRankRegister.register_class("1304", rank_1304)
    # 相里要
    DamageRankRegister.register_class("1305", rank_1305)

    # 忌炎
    DamageRankRegister.register_class("1404", rank_1404)

    # 守岸人
    DamageRankRegister.register_class("1505", rank_1505)

    # 丹瑾
    DamageRankRegister.register_class("1602", rank_1602)
    # 椿
    DamageRankRegister.register_class("1603", rank_1603)
    # 暗主女
    DamageRankRegister.register_class("1604", rank_1604)
    # 暗主男
    DamageRankRegister.register_class("1605", rank_1604)
