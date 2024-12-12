from typing import Dict

from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsStrConfig, GsListStrConfig, GsBoolConfig, GsDictConfig, GsListConfig, )

CONFIG_DEFAULT: Dict[str, GSC] = {
    'WavesAnnGroups': GsDictConfig(
        '推送公告群组',
        '鸣潮公告推送群组',
        {},
    ),
    'WavesAnnNewIds': GsListConfig(
        '推送公告ID',
        '鸣潮公告推送ID列表',
        [],
    ),
    'WavesRankUseTokenGroup': GsListStrConfig(
        '有token才能进排行，群管理可设置',
        '有token才能进排行，群管理可设置',
        [],
    ),
    'WavesRankNoLimitGroup': GsListStrConfig(
        '无限制进排行，群管理可设置',
        '无限制进排行，群管理可设置',
        [],
    ),
    'WavesPrefix': GsStrConfig(
        '插件命令前缀（确认无冲突再修改）',
        '用于设置WutheringWavesUID前缀的配置',
        'ww',
    ),
    'SignTime': GsListStrConfig(
        '每晚签到时间设置',
        '每晚库街区签到时间设置（时，分）',
        ['0', '10'],
    ),
    'SchedSignin': GsBoolConfig(
        '定时签到',
        '开启后每晚00:10将开始自动签到任务',
        True,
    ),
    'BBSSchedSignin': GsBoolConfig(
        '定时库街区每日任务',
        '开启后每晚00:20将开始自动库街区每日任务',
        True,
    ),
    'PrivateSignReport': GsBoolConfig(
        '签到私聊报告',
        '关闭后将不再给任何人推送当天签到任务完成情况',
        False,
    ),
    'SigninMaster': GsBoolConfig(
        '全部开启签到',
        '开启后自动帮登录的人签到',
        False,
    ),
    "CrazyNotice": GsBoolConfig(
        "催命模式",
        "开启后当达到推送阈值将会一直推送",
        False
    ),
    "WavesGuideProvide": GsStrConfig(
        "角色攻略图提供方",
        "使用ww角色攻略时选择的提供方",
        "Moealkyne",
        options=["all", "Moealkyne", "小沐XMu", "金铃子攻略组", "結星"]
    ),
    'WavesLoginUrl': GsStrConfig(
        '鸣潮登录url',
        '用于设置WutheringWavesUID登录界面的配置',
        '',
    ),
    'WavesLoginUrlSelf': GsBoolConfig(
        '强制【鸣潮登录url】为自己的域名',
        '强制【鸣潮登录url】为自己的域名',
        False,
    ),
    'WavesOnlySelfCk': GsBoolConfig(
        '所有查询使用自己的ck',
        '所有查询使用自己的ck',
        False,
    ),
    'BotRank': GsBoolConfig(
        'bot排行',
        'bot排行',
        False,
    ),
    'QQPicCache': GsBoolConfig(
        '排行榜qq头像缓存开关',
        '排行榜qq头像缓存开关',
        False,
    ),
    'RankUseToken': GsBoolConfig(
        '有token才能进排行',
        '有token才能进排行',
        False,
    ),
    'DelInvalidCookie': GsBoolConfig(
        '每天定时删除无效token',
        '每天定时删除无效token',
        False,
    ),
}
