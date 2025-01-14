from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe
from ..utils.database.models import WavesUser, WavesPush

PUSH_MAP = {
    '体力': 'resin',
}
SIGN_MAP = {
    "自动签到": "sign",
    "自动社区签到": "bbs_sign",
    "推送": "push",
}
WAVES_USER_MAP = {
    "体力背景": "stamina_bg"
}

task_name_sign = '订阅鸣潮签到'
task_name_resin = '订阅体力推送'


async def set_waves_user_value(ev: Event, func: str, uid: str, value: str):
    if func in WAVES_USER_MAP:
        status = WAVES_USER_MAP[func]
    else:
        return '该配置项不存在!\n'
    logger.info('[设置{}] uid:{} value: {}'.format(func, uid, value))
    if (
        await WavesUser.update_data_by_data(
            select_data={
                'user_id': ev.user_id,
                'bot_id': ev.bot_id,
                'uid': uid
            },
            update_data={
                f'{status}_value': value
            }
        )
        == 0
    ):
        return f'设置成功!\n特征码[{uid}]\n当前{func}:{value}\n'
    else:
        return '设置失败!\n请检查参数是否正确!\n'


async def set_push_value(bot_id: str, func: str, uid: str, value: int):
    if func in PUSH_MAP:
        status = PUSH_MAP[func]
    else:
        return '该配置项不存在!\n'
    logger.info('[设置推送阈值]func: {}, value: {}'.format(status, value))
    if (
        await WavesPush.update_data_by_uid(
            uid=uid, bot_id=bot_id, **{f'{status}_value': value}
        )
        == 0
    ):
        return f'设置成功!\n当前{func}推送阈值:{value}\n'
    else:
        return '设置失败!\n请检查参数是否正确!\n'


async def set_config_func(ev: Event, uid: str = "0"):
    config_name = ev.text
    if '开启' in ev.command:
        option = ev.group_id if ev.group_id else 'on'
    else:
        option = 'off'

    logger.info(f"uid: {uid}, option: {option}, config_name: {config_name}")

    other_msg = ""

    if config_name in SIGN_MAP:
        # 执行设置
        await WavesUser.update_data_by_uid(
            uid=uid,
            bot_id=ev.bot_id,
            **{f"{SIGN_MAP[config_name]}_switch": option, },
        )
        if config_name == "自动签到" and option != "off":
            await WavesUser.update_data_by_uid(
                uid=uid,
                bot_id=ev.bot_id,
                **{f"{SIGN_MAP['自动社区签到']}_switch": option, },
            )
        if option == 'off':
            await gs_subscribe.delete_subscribe('single', task_name_sign, ev)
        else:
            if config_name == "自动签到" == '自动签到':
                from . import WutheringWavesConfig
                SIGN_TIME = WutheringWavesConfig.get_config('SignTime').data
                other_msg = f"😄将于[{SIGN_TIME[0]}:{SIGN_TIME[1]}]点自动为您开始签到"
            await gs_subscribe.add_subscribe('single', task_name_sign, ev)
    elif config_name.replace('推送', '') in PUSH_MAP:
        await WavesPush.update_data_by_uid(
            uid=uid,
            bot_id=ev.bot_id,
            **{f'{PUSH_MAP[config_name.replace("推送", "")]}_push': option, },
        )
        if option == 'off':
            await gs_subscribe.delete_subscribe('single', task_name_resin, ev)
        else:
            await gs_subscribe.add_subscribe('single', task_name_resin, ev)
    else:
        return "该配置项不存在!"

    if option == "on":
        succeed_msg = "开启至私聊消息!"
    elif option == "off":
        succeed_msg = "关闭!"
    else:
        succeed_msg = f"开启至群{option}"

    return f"{config_name}已{succeed_msg}\n{other_msg}"
