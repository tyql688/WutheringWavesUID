import asyncio
import random
import re
import string

import httpx
from async_timeout import timeout
from pydantic import BaseModel
from starlette.responses import HTMLResponse

from gsuid_core.bot import Bot
from gsuid_core.config import core_config
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.web_app import app
from ..utils.cache import TimedCache
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_103
from ..utils.kuro_api import kuro_api
from ..utils.resource.RESOURCE_PATH import waves_templates
from ..wutheringwaves_config import PREFIX
from ..wutheringwaves_user import deal

cache = TimedCache(timeout=600, maxsize=10)
sv_kuro_login = SV("库洛登录")


async def get_url():
    HOST = core_config.get_config('HOST')
    PORT = core_config.get_config('PORT')

    if HOST == 'localhost' or HOST == '127.0.0.1':
        _host = 'localhost'
    else:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    'https://api.ipify.org/?format=json', timeout=4
                )
            _host = r.json()['ip']
        except:  # noqa:E722, B001
            _host = HOST

    return f'http://{_host}:{PORT}'


def is_valid_chinese_phone_number(phone_number):
    # 正则表达式匹配中国大陆的手机号
    pattern = re.compile(r'^1[3-9]\d{9}$')
    return pattern.match(phone_number) is not None


@sv_kuro_login.on_command(f"{PREFIX}登录")
async def get_resp_msg(bot: Bot, ev: Event):
    game_title = "[鸣潮]"

    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return await bot.send(ERROR_CODE[WAVES_CODE_103])

    text = re.sub(r'["\n\t ]+', '', ev.text.strip())
    text = text.replace("，", ",")
    if text == "":
        auth = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        await bot.send(
            f"请复制地址到浏览器打开：\n{await get_url()}/waves/i/{auth}\n您的id为【${ev.user_id}】\n登录地址10分钟内有效")
        # 手机登录
        data = {"mobile": -1, "code": -1}
        cache.set(auth, data)
        async with timeout(600):
            while True:
                result = cache.get(auth)
                if result is None:
                    return await bot.send("登录超时!")
                if result.get("mobile") != -1 and result.get("code") != -1:
                    text = f"{result['mobile']},{result['code']}"
                    break
                await asyncio.sleep(1)

    if "," in text:
        # 手机+验证码
        try:
            phone_number, code = text.split(",")
            if not is_valid_chinese_phone_number(phone_number):
                raise ValueError("Invalid phone number")
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

    return await bot.send(f"{game_title} 账号登录失败")


@app.get("/waves/i/{auth}")
async def waves_login_index(auth: str):
    if cache.get(auth) is None:
        return HTMLResponse("<h1>登录超时!</h1>")
    template = waves_templates.get_template("index.html")
    return HTMLResponse(template.render(server_url=await get_url(), auth=auth))


class LoginModel(BaseModel):
    auth: str
    mobile: str
    code: str


@app.post("/waves/login")
async def waves_login(data: LoginModel):
    if cache.get(data.auth) is None:
        return HTMLResponse("<h1>登录超时!</h1>")
    cache.set(data.auth, data.dict())
    cache.delete(data.auth)
