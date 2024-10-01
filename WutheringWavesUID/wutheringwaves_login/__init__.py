import re

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .login import page_login, code_login
from ..utils.database.models import WavesBind
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_103
from ..wutheringwaves_config import PREFIX

sv_kuro_login = SV("库洛登录")


@sv_kuro_login.on_command(f"{PREFIX}登录")
async def get_resp_msg(bot: Bot, ev: Event):
    game_title = "[鸣潮]"

    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    text = re.sub(r'["\n\t ]+', '', ev.text.strip())
    text = text.replace("，", ",")
    if text == "":
        return await page_login(bot, ev)

    if "," in text:
        return await code_login(bot, ev, text)

    return await bot.send(f"{game_title} 账号登录失败")
