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
    'WavesPrefix': GsStrConfig(
        '插件命令前缀（确认无冲突再修改）',
        '用于设置WutheringWavesUID前缀的配置',
        'ww',
    ),
    'SignTime': GsListStrConfig(
        '每晚签到时间设置',
        '每晚米游社签到时间设置（时，分）',
        ['0', '10'],
    ),
    'SchedSignin': GsBoolConfig(
        '定时签到',
        '开启后每晚00:10将开始自动签到任务',
        True,
    ),
    'PrivateSignReport': GsBoolConfig(
        '签到私聊报告',
        '关闭后将不再给任何人推送当天签到任务完成情况',
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
        options=["all", "Moealkyne", "小沐XMu"]
    ),
    'WavesLoginUrl': GsStrConfig(
        '鸣潮登录url',
        '用于设置WutheringWavesUID登录界面的配置',
        '',
    ),
}
