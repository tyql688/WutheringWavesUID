from ....utils.damage.abstract import DamageDetailRegister


def register_damage():
    from ....utils.map.damage.damage_1205 import damage_detail as damage_1205
    from ....utils.map.damage.damage_1302 import damage_detail as damage_1302
    from ....utils.map.damage.damage_1304 import damage_detail as damage_1304
    from ....utils.map.damage.damage_1305 import damage_detail as damage_1305
    from ....utils.map.damage.damage_1404 import damage_detail as damage_1404
    from ....utils.map.damage.damage_1602 import damage_detail as damage_1602
    from ....utils.map.damage.damage_1603 import damage_detail as damage_1603
    from ....utils.map.damage.damage_1604 import damage_detail as damage_1604

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
    # 丹瑾
    DamageDetailRegister.register_class("1602", damage_1602)
    # 椿
    DamageDetailRegister.register_class("1603", damage_1603)
    # 暗主女
    DamageDetailRegister.register_class("1604", damage_1604)
    # 暗主男
    DamageDetailRegister.register_class("1605", damage_1604)
