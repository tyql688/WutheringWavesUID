import re

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_103
from ..utils.kuro_api import kuro_api
from ..wutheringwaves_config import PREFIX
from ..wutheringwaves_user import deal

sv_kuro_login = SV("库洛登录", area='DIRECT')


@sv_kuro_login.on_prefix(f"{PREFIX}登录")
async def get_resp_msg(bot: Bot, ev: Event):
    game_title = "[鸣潮]"

    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    text = re.sub(r'["\n\t ]+', '', ev.text.strip())
    text = text.replace("，", ",")
    if "," in text:
        # 手机+验证码
        try:
            phone_number, code = text.split(",")
        except ValueError as _:
            return await bot.send(
                f"{game_title} 手机号+验证码登录失败\n\n请参照以下格式:\n{PREFIX}登录 手机号,验证码")

        result = await kuro_api.login(phone_number, code)
        if not isinstance(result, dict) or result.get('code') != 200 or result.get('data') is None:
            return await bot.send(result.get("msg", f"{game_title} 验证码登录失败\n"))
        token = result.get('data', {}).get("token", '')
        ck_res = await deal.add_cookie(ev, token)
        if "成功" in ck_res:
            user = await WavesUser.get_user_by_attr(ev.user_id, ev.bot_id, 'cookie', token)
            if user:
                await WavesBind.insert_uid(ev.user_id, ev.bot_id, user.uid, ev.group_id, lenth_limit=9)
            return await bot.send(f"{game_title} 登录成功!")
    else:
        return await bot.send(f"{game_title} 账号登录失败\n\n请参照以下格式:\n{PREFIX}登录 手机号,验证码")
        # 手机登录
        # phone_number = text
        # if not phone_number.isdigit():
        #     return await bot.send("你输入了错误的格式!")
        # resp = await bot.receive_resp(
        #     f"请确认你的手机号码: {phone_number}." "如果正确请回复'确认', 其他任何回复将取消本次操作."
        # )
        # if resp is not None and resp.text == "确认":
        #     result = await kuro_api.send_phone_code(phone_number)
        #     return await bot.send(json.dumps(result))

    return await bot.send("登录成功!")
