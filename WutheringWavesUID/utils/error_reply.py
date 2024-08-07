from ..utils.waves_prefix import PREFIX

WAVES_CODE_100 = -100
WAVES_CODE_101 = -101
WAVES_CODE_102 = -102
WAVES_CODE_103 = -103
WAVES_CODE_104 = -104
WAVES_CODE_105 = -105
WAVES_CODE_200 = -200
WAVES_CODE_201 = -201
WAVES_CODE_202 = -202
WAVES_CODE_203 = -203
WAVES_CODE_204 = -204
WAVES_CODE_998 = -998
WAVES_CODE_999 = -999

ERROR_CODE = {
    WAVES_CODE_100: "库街区未查询到您的游戏角色，请检查是否对外访问",
    WAVES_CODE_101: "请检查ck有效性",
    WAVES_CODE_102: f"您还未绑定鸣潮ck, 请使用 {PREFIX}添加CK 完成绑定！",
    WAVES_CODE_103: f"您还未绑定鸣潮id, 请使用 {PREFIX}绑定UID 完成绑定！",
    WAVES_CODE_104: f"请保证抽卡链接的uid与当前正在使用的uid一致\n\n请使用以下命令核查:\n{PREFIX}查看UID\n{PREFIX}切换UID123456",
    WAVES_CODE_105: f"您还未导入鸣潮抽卡链接\n\n请使用以下命令核查:\n{PREFIX}导入抽卡链接",

    WAVES_CODE_200: "当前TapTap账号未绑定鸣潮角色",
    WAVES_CODE_201: "未获取到TapTap账号绑定的鸣潮角色信息",
    WAVES_CODE_202: "请您绑定自己的TapTap账号",
    WAVES_CODE_203: f"您还未绑定TapTap账号, 请使用 {PREFIX}绑定tap 完成绑定！",
    WAVES_CODE_204: "TapTap强制刷新面板失败，请检查您的TapTap账号是否已经解绑鸣潮",

    WAVES_CODE_998: "请求TapTap错误，先看看日志吧",
    WAVES_CODE_999: "不知道的错误，先看看日志吧"
}
