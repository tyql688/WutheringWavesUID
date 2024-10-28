from ..utils.waves_prefix import PREFIX

WAVES_CODE_100 = -100
WAVES_CODE_101 = -101
WAVES_CODE_102 = -102
WAVES_CODE_103 = -103
WAVES_CODE_104 = -104
WAVES_CODE_105 = -105
WAVES_CODE_106 = -106
WAVES_CODE_107 = -107
WAVES_CODE_108 = -108
WAVES_CODE_998 = -998
WAVES_CODE_999 = -999

ERROR_CODE = {
    WAVES_CODE_100: "库街区未查询到您的游戏角色，请检查是否对外访问",
    WAVES_CODE_101: "请检查ck有效性",
    WAVES_CODE_102: f"您还未绑定鸣潮ck或者您的鸣潮ck已失效！\n 请使用 {PREFIX}登录 或者 {PREFIX}添加CK 完成绑定！",
    WAVES_CODE_103: f"您还未绑定鸣潮id, 请使用 {PREFIX}绑定UID 完成绑定！",
    WAVES_CODE_104: f"请保证抽卡链接的uid与当前正在使用的uid一致\n\n请使用以下命令核查:\n{PREFIX}查看UID\n{PREFIX}切换UID123456",
    WAVES_CODE_105: f"您还未导入鸣潮抽卡链接\n\n请使用以下命令核查:\n{PREFIX}导入抽卡链接",
    WAVES_CODE_106: f"您未打开库街区我得资料的对外展示\n",
    WAVES_CODE_107: f"您未打开库街区共鸣者列表的对外展示\n",
    WAVES_CODE_108: f"当前抽卡链接已经失效，请重新导入抽卡链接\n",

    WAVES_CODE_999: "不知道的错误，先看看日志吧"
}
