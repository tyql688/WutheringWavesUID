from ....utils.damage.abstract import DamageDetailRegister, DamageRankRegister


def register_damage():
    from .damage_1102 import damage_detail as damage_1102
    from .damage_1103 import damage_detail as damage_1103
    from .damage_1104 import damage_detail as damage_1104
    from .damage_1105 import damage_detail as damage_1105
    from .damage_1106 import damage_detail as damage_1106
    from .damage_1107 import damage_detail as damage_1107
    from .damage_1202 import damage_detail as damage_1202
    from .damage_1203 import damage_detail as damage_1203
    from .damage_1204 import damage_detail as damage_1204
    from .damage_1205 import damage_detail as damage_1205
    from .damage_1206 import damage_detail as damage_1206
    from .damage_1207 import damage_detail as damage_1207
    from .damage_1301 import damage_detail as damage_1301
    from .damage_1302 import damage_detail as damage_1302
    from .damage_1303 import damage_detail as damage_1303
    from .damage_1304 import damage_detail as damage_1304
    from .damage_1305 import damage_detail as damage_1305
    from .damage_1402 import damage_detail as damage_1402
    from .damage_1403 import damage_detail as damage_1403
    from .damage_1404 import damage_detail as damage_1404
    from .damage_1405 import damage_detail as damage_1405
    from .damage_1406 import damage_detail as damage_1406
    from .damage_1407 import damage_detail as damage_1407
    from .damage_1409 import damage_detail as damage_1409
    from .damage_1502 import damage_detail as damage_1502
    from .damage_1503 import damage_detail as damage_1503
    from .damage_1504 import damage_detail as damage_1504
    from .damage_1505 import damage_detail as damage_1505
    from .damage_1506 import damage_detail as damage_1506
    from .damage_1507 import damage_detail as damage_1507
    from .damage_1601 import damage_detail as damage_1601
    from .damage_1602 import damage_detail as damage_1602
    from .damage_1603 import damage_detail as damage_1603
    from .damage_1604 import damage_detail as damage_1604
    from .damage_1606 import damage_detail as damage_1606
    from .damage_1607 import damage_detail as damage_1607

    # 散华
    DamageDetailRegister.register_class("1102", damage_1102)
    # 白芷
    DamageDetailRegister.register_class("1103", damage_1103)
    # 凌阳
    DamageDetailRegister.register_class("1104", damage_1104)
    # 折枝
    DamageDetailRegister.register_class("1105", damage_1105)
    # 釉瑚
    DamageDetailRegister.register_class("1106", damage_1106)
    # 珂莱塔
    DamageDetailRegister.register_class("1107", damage_1107)

    # 炽霞
    DamageDetailRegister.register_class("1202", damage_1202)
    # 安可
    DamageDetailRegister.register_class("1203", damage_1203)
    # 莫特斐
    DamageDetailRegister.register_class("1204", damage_1204)
    # 长离
    DamageDetailRegister.register_class("1205", damage_1205)
    # 布兰特
    DamageDetailRegister.register_class("1206", damage_1206)
    # 露帕
    DamageDetailRegister.register_class("1207", damage_1207)

    # 卡卡罗
    DamageDetailRegister.register_class("1301", damage_1301)
    # 吟霖
    DamageDetailRegister.register_class("1302", damage_1302)
    # 渊武
    DamageDetailRegister.register_class("1303", damage_1303)
    # 今汐
    DamageDetailRegister.register_class("1304", damage_1304)
    # 相里要
    DamageDetailRegister.register_class("1305", damage_1305)

    # 秧秧
    DamageDetailRegister.register_class("1402", damage_1402)
    # 秋水
    DamageDetailRegister.register_class("1403", damage_1403)
    # 忌炎
    DamageDetailRegister.register_class("1404", damage_1404)
    # 鉴心
    DamageDetailRegister.register_class("1405", damage_1405)
    # 风主男
    DamageDetailRegister.register_class("1406", damage_1406)
    # 夏空
    DamageDetailRegister.register_class("1407", damage_1407)
    # 风主女
    DamageDetailRegister.register_class("1408", damage_1406)
    # 卡提希娅
    DamageDetailRegister.register_class("1409", damage_1409)

    # 光主男
    DamageDetailRegister.register_class("1501", damage_1502)
    # 光主女
    DamageDetailRegister.register_class("1502", damage_1502)
    # 维里奈
    DamageDetailRegister.register_class("1503", damage_1503)
    # 灯灯
    DamageDetailRegister.register_class("1504", damage_1504)
    # 守岸人
    DamageDetailRegister.register_class("1505", damage_1505)
    # 菲比
    DamageDetailRegister.register_class("1506", damage_1506)
    # 赞妮
    DamageDetailRegister.register_class("1507", damage_1507)

    # 桃祈
    DamageDetailRegister.register_class("1601", damage_1601)
    # 丹瑾
    DamageDetailRegister.register_class("1602", damage_1602)
    # 椿
    DamageDetailRegister.register_class("1603", damage_1603)
    # 暗主女
    DamageDetailRegister.register_class("1604", damage_1604)
    # 暗主男
    DamageDetailRegister.register_class("1605", damage_1604)
    # 洛可可
    DamageDetailRegister.register_class("1606", damage_1606)
    # 坎特蕾拉
    DamageDetailRegister.register_class("1607", damage_1607)


def register_rank():
    from .damage_1102 import rank as rank_1102
    from .damage_1103 import rank as rank_1103
    from .damage_1104 import rank as rank_1104
    from .damage_1105 import rank as rank_1105
    from .damage_1106 import rank as rank_1106
    from .damage_1107 import rank as rank_1107
    from .damage_1202 import rank as rank_1202
    from .damage_1203 import rank as rank_1203
    from .damage_1204 import rank as rank_1204
    from .damage_1205 import rank as rank_1205
    from .damage_1206 import rank as rank_1206
    from .damage_1301 import rank as rank_1301
    from .damage_1302 import rank as rank_1302
    from .damage_1303 import rank as rank_1303
    from .damage_1304 import rank as rank_1304
    from .damage_1305 import rank as rank_1305
    from .damage_1402 import rank as rank_1402
    from .damage_1403 import rank as rank_1403
    from .damage_1404 import rank as rank_1404
    from .damage_1405 import rank as rank_1405
    from .damage_1406 import rank as rank_1406
    from .damage_1407 import rank as rank_1407
    from .damage_1409 import rank as rank_1409
    from .damage_1502 import rank as rank_1502
    from .damage_1503 import rank as rank_1503
    from .damage_1504 import rank as rank_1504
    from .damage_1505 import rank as rank_1505
    from .damage_1506 import rank as rank_1506
    from .damage_1507 import rank as rank_1507
    from .damage_1601 import rank as rank_1601
    from .damage_1602 import rank as rank_1602
    from .damage_1603 import rank as rank_1603
    from .damage_1604 import rank as rank_1604
    from .damage_1606 import rank as rank_1606
    from .damage_1607 import rank as rank_1607

    # 散华
    DamageRankRegister.register_class("1102", rank_1102)
    # 白芷
    DamageRankRegister.register_class("1103", rank_1103)
    # 凌阳
    DamageRankRegister.register_class("1104", rank_1104)
    # 折枝
    DamageRankRegister.register_class("1105", rank_1105)
    # 釉瑚
    DamageRankRegister.register_class("1106", rank_1106)
    # 珂莱塔
    DamageRankRegister.register_class("1107", rank_1107)

    # 炽霞
    DamageRankRegister.register_class("1202", rank_1202)
    # 安可
    DamageRankRegister.register_class("1203", rank_1203)
    # 莫特斐
    DamageRankRegister.register_class("1204", rank_1204)
    # 长离
    DamageRankRegister.register_class("1205", rank_1205)
    # 布兰特
    DamageRankRegister.register_class("1206", rank_1206)

    # 卡卡罗
    DamageRankRegister.register_class("1301", rank_1301)
    # 吟霖
    DamageRankRegister.register_class("1302", rank_1302)
    # 渊武
    DamageRankRegister.register_class("1303", rank_1303)
    # 今汐
    DamageRankRegister.register_class("1304", rank_1304)
    # 相里要
    DamageRankRegister.register_class("1305", rank_1305)

    # 秧秧
    DamageRankRegister.register_class("1402", rank_1402)
    # 秋水
    DamageRankRegister.register_class("1403", rank_1403)
    # 忌炎
    DamageRankRegister.register_class("1404", rank_1404)
    # 鉴心
    DamageRankRegister.register_class("1405", rank_1405)
    # 风主男
    DamageRankRegister.register_class("1406", rank_1406)
    # 夏空
    DamageRankRegister.register_class("1407", rank_1407)
    # 风主女
    DamageRankRegister.register_class("1408", rank_1406)
    # 卡提希娅
    DamageRankRegister.register_class("1409", rank_1409)

    # 光主男
    DamageRankRegister.register_class("1501", rank_1502)
    # 光主女
    DamageRankRegister.register_class("1502", rank_1502)
    # 维里奈
    DamageRankRegister.register_class("1503", rank_1503)
    # 灯灯
    DamageRankRegister.register_class("1504", rank_1504)
    # 守岸人
    DamageRankRegister.register_class("1505", rank_1505)
    # 菲比
    DamageRankRegister.register_class("1506", rank_1506)
    # 赞妮
    DamageRankRegister.register_class("1507", rank_1507)
    # 桃祈
    DamageRankRegister.register_class("1601", rank_1601)
    # 丹瑾
    DamageRankRegister.register_class("1602", rank_1602)
    # 椿
    DamageRankRegister.register_class("1603", rank_1603)
    # 暗主女
    DamageRankRegister.register_class("1604", rank_1604)
    # 暗主男
    DamageRankRegister.register_class("1605", rank_1604)
    # 洛可可
    DamageRankRegister.register_class("1606", rank_1606)
    # 坎特蕾拉
    DamageRankRegister.register_class("1607", rank_1607)
