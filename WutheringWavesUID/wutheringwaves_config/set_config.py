from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe

from ..utils.database.models import WavesPush, WavesUser
from datetime import datetime
import time

PUSH_MAP = {
    "体力": "resin",
    "时间": "push_time",
}
WAVES_USER_MAP = {"体力背景": "stamina_bg"}

task_name_resin = "订阅体力推送"

async def get_push_config():
    from ..wutheringwaves_config import WutheringWavesConfig

    return WutheringWavesConfig.get_config("StaminaPush").data

async def set_waves_user_value(ev: Event, func: str, uid: str, value: str):
    if func in WAVES_USER_MAP:
        status = WAVES_USER_MAP[func]
    else:
        return "该配置项不存在!\n"
    logger.info("[设置{}] uid:{} value: {}".format(func, uid, value))
    if (
        await WavesUser.update_data_by_data(
            select_data={"user_id": ev.user_id, "bot_id": ev.bot_id, "uid": uid},
            update_data={f"{status}_value": value},
        )
        == 0
    ):
        return f"设置成功!\n特征码[{uid}]\n当前{func}:{value}\n"
    else:
        return "设置失败!\n请检查参数是否正确!\n"

async def set_push_value(ev: Event, func: str, uid: str, value: int):
    if func in PUSH_MAP:
        status = PUSH_MAP[func]
    else:
        return "该配置项不存在!\n"
    logger.info("[设置推送阈值]func: {}, value: {}".format(status, value))
    if (
        await WavesPush.update_data_by_uid(
            uid=uid, bot_id=ev.bot_id, **{f"{status}_value": value}
        )
        == 0
    ):
        data = await WavesPush.select_data_by_uid(uid)
        push_data = data.__dict__
        if not push_data["push_time_value"]:
            logger.info("[开启体力推送] uid:{}".format(uid))
            option = ev.group_id if ev.group_id else "on"
            await WavesUser.update_data_by_uid(
                uid=uid, bot_id=ev.bot_id, **{"push_switch": option},
            )
            await WavesPush.update_data_by_uid(
                uid=uid, bot_id=ev.bot_id, **{f"{PUSH_MAP['体力']}_push": option},
            )
            timestamp = time.time()
            time_push = datetime.fromtimestamp(int(timestamp))
            await WavesPush.update_data_by_uid(
                uid=uid, bot_id=ev.bot_id, **{f"{PUSH_MAP['时间']}_value": time_push}
            )

        return f"设置成功!\n当前{func}推送阈值:{value}\n"
    else:
        return "设置失败!\n请检查参数是否正确!\n"


async def set_push_time(bot_id: str, uid: str, value: int):
    """传入满体力时时间戳设置推送时间"""
    func = "时间"
    mode = "resin"

    if func in PUSH_MAP:
        status = PUSH_MAP[func]
    else:
        logger.info("该配置项不存在!")
        return False
    
    data = await WavesPush.select_data_by_uid(uid)
    if not data: 
        return False
    push_data = data.__dict__
    resin_push = push_data[f"{mode}_value"]

    # 根据体力阈值计算推送时间
    value = value - (240 -resin_push) * 6 * 60
    time_push = datetime.fromtimestamp(int(value))

    logger.info("[设置推送时间]func: {}, value: {}".format(status, time_push))
    try:
        await WavesPush.update_data_by_uid(
            uid=uid, bot_id=bot_id, **{f"{status}_value": time_push}
        )
        await WavesPush.update_data_by_uid(
            uid=uid, bot_id=bot_id, **{f"{mode}_is_push": "off"}
        )
        logger.info(f"设置成功!\n当前{func}推送阈值:{time_push}\n")
        return True
    except Exception as e:
        logger.info(f"[推送时间]设置失败:{e}")
        return False



async def set_config_func(ev: Event, uid: str = "0"):
    config_name = ev.text
    if "开启" in ev.command:
        option = ev.group_id if ev.group_id else "on"
    else:
        option = "off"

    logger.info(f"uid: {uid}, option: {option}, config_name: {config_name}")

    other_msg = ""

    if config_name.replace("推送", "") in PUSH_MAP:
        if not await get_push_config():
            return "体力推送功能已禁用!\n"

         # 执行设置
        await WavesUser.update_data_by_uid(
            uid=uid,
            bot_id=ev.bot_id,
            **{
                "push_switch": option,
            },
        )
        await WavesPush.update_data_by_uid(
            uid=uid,
            bot_id=ev.bot_id,
            **{
                f"{PUSH_MAP[config_name.replace('推送', '')]}_push": option,
            },
        )
        timestamp = time.time()
        time_push = datetime.fromtimestamp(int(timestamp))
        await WavesPush.update_data_by_uid(
            uid=uid, bot_id=ev.bot_id, **{f"{PUSH_MAP['时间']}_value": time_push}
        )
        if option == "off":
            await gs_subscribe.delete_subscribe("single", task_name_resin, ev)
        else:
            await gs_subscribe.add_subscribe("single", task_name_resin, ev)
    else:
        return "该配置项不存在!"

    if option == "on":
        succeed_msg = "开启至私聊消息!"
    elif option == "off":
        succeed_msg = "关闭!"
    else:
        succeed_msg = f"开启至群{option}"

    return f"{config_name}已{succeed_msg}\n{other_msg}"
