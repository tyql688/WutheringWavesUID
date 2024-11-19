from ....utils.damage.abstract import DamageDetailRegister


def register_damage():
    from ....utils.map.damage.damage_1205 import damage_detail as damage_1205
    from ....utils.map.damage.damage_1404 import damage_detail as damage_1404
    from ....utils.map.damage.damage_1603 import damage_detail as damage_1603

    # 长离
    DamageDetailRegister.register_class("1205", damage_1205)
    # 忌炎
    DamageDetailRegister.register_class("1404", damage_1404)
    # 椿
    DamageDetailRegister.register_class("1603", damage_1603)
