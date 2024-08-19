from typing import Dict

from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsStrConfig, GsListStrConfig, GsBoolConfig,
)

CONFIG_DEFAULT: Dict[str, GSC] = {
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
}
