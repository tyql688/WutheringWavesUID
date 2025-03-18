from ..wutheringwaves_config import PREFIX

WAVES_CODE_100 = -100
WAVES_CODE_101 = -101
WAVES_CODE_102 = -102
WAVES_CODE_103 = -103
WAVES_CODE_104 = -104
WAVES_CODE_105 = -105
WAVES_CODE_106 = -106
WAVES_CODE_107 = -107
WAVES_CODE_108 = -108
WAVES_CODE_109 = -109
WAVES_CODE_998 = -998
WAVES_CODE_999 = -999

ERROR_CODE = {
    WAVES_CODE_100: "库街区未查询到您的游戏角色，请检查是否对外访问\n",
    WAVES_CODE_101: "请检查token有效性\n",
    WAVES_CODE_102: f"您还未绑定鸣潮token或者您的鸣潮token已失效！\n请使用【{PREFIX}登录】完成绑定！\n",
    WAVES_CODE_103: f"您还未绑定鸣潮特征码, 请使用【{PREFIX}绑定uid】完成绑定！\n",
    WAVES_CODE_104: f"请保证抽卡链接的特征码与当前正在使用的特征码一致\n\n请使用以下命令核查:\n{PREFIX}查看\n{PREFIX}切换123456\n",
    WAVES_CODE_105: f"您还未导入鸣潮抽卡链接\n\n请使用以下命令核查:【{PREFIX}导入抽卡链接】\n",
    WAVES_CODE_106: "您未打开库街区我得资料的对外展示\n",
    WAVES_CODE_107: "您未打开库街区共鸣者列表的对外展示\n",
    WAVES_CODE_108: "当前抽卡链接已经失效，请重新导入抽卡链接\n",
    WAVES_CODE_998: "IP可能被封禁，请检查是否存在违规行为\n",
    WAVES_CODE_999: "不知道的错误，先看看日志吧",
}
