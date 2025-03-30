import asyncio
import re

from async_timeout import timeout

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV

from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import (
    ERROR_CODE,
    WAVES_CODE_103,
    WAVES_CODE_104,
    WAVES_CODE_105,
)
from ..utils.hint import error_reply
from ..wutheringwaves_config import PREFIX
from .draw_gachalogs import draw_card, draw_card_help
from .get_gachalogs import export_gachalogs, import_gachalogs, save_gachalogs

sv_gacha_log = SV("waves抽卡记录")
sv_gacha_help_log = SV("waves抽卡记录帮助")
sv_get_gachalog_by_link = SV("waves导入抽卡链接", area="DIRECT")
sv_import_gacha_log = SV("waves导入抽卡记录", area="DIRECT")
sv_export_json_gacha_log = SV("waves导出抽卡记录")


@sv_get_gachalog_by_link.on_command(("导入抽卡链接", "导入抽卡记录"))
async def get_gacha_log_by_link(bot: Bot, ev: Event):

    # 没有uid 就别导了吧
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    raw = ev.text.strip()
    if not raw:
        try:
            at_sender = True if ev.group_id else False
            await bot.send("请于30s内给出正确的抽卡记录链接", at_sender)
            async with timeout(30):
                while True:
                    resp = await bot.receive_resp(timeout=30)
                    if resp is not None:
                        raw = resp.text
                        break
        except asyncio.TimeoutError:
            await bot.send(f"时间到！请重新发送 {PREFIX}导入抽卡链接", at_sender)

    text = re.sub(r'["\n\t ]+', "", raw)
    if "https://" in text:
        # 使用正则表达式匹配参数
        match_record_id = re.search(r"record_id=([a-zA-Z0-9]+)", text)
        match_player_id = re.search(r"player_id=(\d+)", text)
    elif "{" in text:
        match_record_id = re.search(r"recordId:([a-zA-Z0-9]+)", text)
        match_player_id = re.search(r"playerId:(\d+)", text)
    elif "recordId=" in text:
        match_record_id = re.search(r"recordId=([a-zA-Z0-9]+)", text)
        match_player_id = re.search(r"playerId=(\d+)", text)
    else:
        match_record_id = re.search(r"recordId=([a-zA-Z0-9]+)", "recordId=" + text)
        match_player_id = ""

    # 提取参数值
    record_id = match_record_id.group(1) if match_record_id else None
    player_id = match_player_id.group(1) if match_player_id else None

    if not record_id or len(record_id) != 32:
        return await bot.send(
            f"请给出正确的抽卡记录链接, 请重新发送 {PREFIX}导入抽卡链接"
        )

    if player_id and player_id != uid:
        logger.info(
            f"[鸣潮]用户：{ev.user_id} 当前抽卡链接与当前绑定的UID不匹配 player_id:{player_id} uid:{uid}"
        )
        return await bot.send(error_reply(WAVES_CODE_104))

    is_force = False
    if ev.command.startswith("强制"):
        await bot.logger.info("[WARNING]本次为强制刷新")
        is_force = True
    await bot.send(f"UID{uid}开始执行[刷新抽卡记录],需要一定时间...请勿重复触发!")
    im = await save_gachalogs(ev, uid, record_id, is_force)
    return await bot.send(im)


@sv_gacha_log.on_fullmatch(
    ("刷新抽卡记录", "更新抽卡记录"),
)
async def send_refresh_gachalog_msg(bot: Bot, ev: Event):
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    user = await WavesUser.get_user_by_attr(ev.user_id, ev.bot_id, "uid", uid)
    if not user or not user.record_id:
        return await bot.send(ERROR_CODE[WAVES_CODE_105])

    await bot.send(f"开始刷新{uid}抽卡记录，需要一定时间，请勿重复执行.....")
    im = await save_gachalogs(ev, uid, user.record_id)
    return await bot.send(im)


@sv_gacha_log.on_fullmatch("抽卡记录")
async def send_gacha_log_card_info(bot: Bot, ev: Event):
    await bot.logger.info("[鸣潮]开始执行 抽卡记录")
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    im = await draw_card(uid, ev)
    await bot.send(im)


@sv_gacha_help_log.on_fullmatch("抽卡帮助")
async def send_gacha_log_help(bot: Bot, ev: Event):
    im = await draw_card_help()
    await bot.send(im)


@sv_import_gacha_log.on_file("json")
async def get_gacha_log_by_file(bot: Bot, ev: Event):
    # 没有uid 就别导了吧
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    if ev.file and ev.file_type:
        await bot.send("正在尝试导入抽卡记录中，请耐心等待……")
        return await bot.send(await import_gachalogs(ev, ev.file, ev.file_type, uid))
    else:
        return await bot.send("导入抽卡记录异常...")


@sv_export_json_gacha_log.on_fullmatch(("导出抽卡记录"))
async def send_export_gacha_info(bot: Bot, ev: Event):
    uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not uid:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    await bot.send("🔜即将为你导出WutheringWavesUID抽卡记录文件，请耐心等待...")
    export = await export_gachalogs(uid)
    if export["retcode"] == "ok":
        file_name = export["name"]
        file_path = export["url"]
        await bot.send(MessageSegment.file(file_path, file_name))
        await bot.send("✅导出抽卡记录成功！")
    else:
        await bot.send("导出抽卡记录失败...")
