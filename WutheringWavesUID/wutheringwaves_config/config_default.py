from typing import Dict

from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsBoolConfig,
    GsDictConfig,
    GsIntConfig,
    GsListConfig,
    GsListStrConfig,
    GsStrConfig,
)

CONFIG_DEFAULT: Dict[str, GSC] = {
    "WavesAnnGroups": GsDictConfig(
        "推送公告群组",
        "鸣潮公告推送群组",
        {},
    ),
    "WavesAnnNewIds": GsListConfig(
        "推送公告ID",
        "鸣潮公告推送ID列表",
        [],
    ),
    "WavesAnnOpen": GsBoolConfig(
        "公告推送总开关",
        "公告推送总开关",
        True,
    ),
    "CrazyNotice": GsBoolConfig("催命模式", "开启后当达到推送阈值将会一直推送", False),
    "StaminaPush": GsBoolConfig(
        "体力推送全局开关", "开启后当体力达到推送阈值将会推送", False
    ),
    "StaminaPushInterval": GsIntConfig(
        "体力推送间隔（分钟）", "体力推送间隔（分钟）", 30, 60
    ),
    "WavesRankUseTokenGroup": GsListStrConfig(
        "有token才能进排行，群管理可设置",
        "有token才能进排行，群管理可设置",
        [],
    ),
    "WavesRankNoLimitGroup": GsListStrConfig(
        "无限制进排行，群管理可设置",
        "无限制进排行，群管理可设置",
        [],
    ),
    "WavesGuide": GsListStrConfig(
        "角色攻略图提供方",
        "使用ww角色攻略时选择的提供方",
        ["all"],
        options=[
            "all",
            "小羊早睡不遭罪",
            "金铃子攻略组",
            "結星",
            "Moealkyne",
            "小沐XMu",
            "吃我无痕",
        ],
    ),
    "GuideSegment": GsBoolConfig("攻略切段", "避免攻略过长过大", False),
    "WavesLoginUrl": GsStrConfig(
        "鸣潮登录url",
        "用于设置WutheringWavesUID登录界面的配置",
        "",
    ),
    "WavesLoginUrlSelf": GsBoolConfig(
        "强制【鸣潮登录url】为自己的域名",
        "强制【鸣潮登录url】为自己的域名",
        False,
    ),
    "WavesTencentWord": GsBoolConfig(
        "腾讯文档",
        "腾讯文档",
        False,
    ),
    "WavesQRLogin": GsBoolConfig(
        "开启后，登录链接变成二维码",
        "开启后，登录链接变成二维码",
        False,
    ),
    "WavesLoginForward": GsBoolConfig(
        "开启后，登录链接变为转发消息",
        "开启后，登录链接变为转发消息",
        False,
    ),
    "WavesOnlySelfCk": GsBoolConfig(
        "所有查询使用自己的ck",
        "所有查询使用自己的ck",
        False,
    ),
    "CardUseOptions2": GsStrConfig(
        "排行面板数据启用规则（重启生效）",
        "排行面板数据启用规则",
        "不使用缓存",
        options=["不使用缓存", "内存缓存"],
    ),
    "QQPicCache": GsBoolConfig(
        "排行榜qq头像缓存开关",
        "排行榜qq头像缓存开关",
        False,
    ),
    "RankUseToken": GsBoolConfig(
        "有token才能进排行",
        "有token才能进排行",
        False,
    ),
    "DelInvalidCookie": GsBoolConfig(
        "每天定时删除无效token",
        "每天定时删除无效token",
        False,
    ),
    "AnnMinuteCheck": GsIntConfig(
        "公告推送时间检测（单位min）", "公告推送时间检测（单位min）", 10, 60
    ),
    "RefreshInterval": GsIntConfig(
        "刷新面板间隔，重启生效（单位秒）",
        "刷新面板间隔，重启生效（单位秒）",
        0,
        600,
    ),
    "RefreshIntervalNotify": GsStrConfig(
        "刷新面板间隔通知文案",
        "刷新面板间隔通知文案",
        "请等待{}s后尝试刷新面板！",
    ),
    "HideUid": GsBoolConfig(
        "隐藏uid",
        "隐藏uid",
        False,
    ),
    "MaxBindNum": GsIntConfig(
        "绑定特征码限制数量（未登录）", "绑定特征码限制数量（未登录）", 2, 100
    ),
    "OCRspaceApiKeyList": GsListStrConfig(
        "OCRspace API Key List",
        "用于ocr识别discord_bot角色卡片",
        [],
        options=[
            "可输入多个key",
            "输入后回车",
        ],
    ),
    "WavesToken": GsStrConfig(
        "鸣潮全排行token",
        "鸣潮全排行token",
        "",
    ),
    "AtCheck": GsBoolConfig(
        "开启可以艾特查询",
        "开启可以艾特查询",
        True,
    ),
    "KuroUrlProxyUrl": GsStrConfig(
        "库洛域名代理（重启生效）",
        "库洛域名代理（重启生效）",
        "",
    ),
    "LocalProxyUrl": GsStrConfig(
        "本地代理地址",
        "本地代理地址",
        "",
    ),
}
