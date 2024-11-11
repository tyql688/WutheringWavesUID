import asyncio
import random
import re
import string
from typing import Union

import httpx
from PIL import ImageDraw
from async_timeout import timeout
from pydantic import BaseModel
from starlette.responses import HTMLResponse

from gsuid_core.bot import Bot
from gsuid_core.config import core_config
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.web_app import app
from ..utils.cache import TimedCache
from ..utils.database.models import WavesUser, WavesBind
from ..utils.fonts.waves_fonts import waves_font_40, waves_font_25
from ..utils.image import get_waves_bg, add_footer
from ..utils.kuro_api import kuro_api
from ..utils.resource.RESOURCE_PATH import waves_templates
from ..utils.util import get_public_ip
from ..wutheringwaves_config import WutheringWavesConfig, PREFIX
from ..wutheringwaves_user import deal

cache = TimedCache(timeout=600, maxsize=10)


async def get_url() -> (str, bool):
    url = WutheringWavesConfig.get_config('WavesLoginUrl').data
    if url:
        if not url.startswith('http'):
            url = f'https://{url}'
        return url, WutheringWavesConfig.get_config('WavesLoginUrlSelf').data
    else:
        HOST = core_config.get_config('HOST')
        PORT = core_config.get_config('PORT')

        if HOST == 'localhost' or HOST == '127.0.0.1':
            _host = 'localhost'
        else:
            _host = await get_public_ip(HOST)

        return f'http://{_host}:{PORT}', True


def is_valid_chinese_phone_number(phone_number):
    # 正则表达式匹配中国大陆的手机号
    pattern = re.compile(r'^1[3-9]\d{9}$')
    return pattern.match(phone_number) is not None


def is_validate_code(code):
    # 正则表达式匹配6位数字
    pattern = re.compile(r'^\d{6}$')
    return pattern.match(code) is not None


async def page_login(bot: Bot, ev: Event):
    at_sender = True if ev.group_id else False

    game_title = "[鸣潮]"
    url, is_local = await get_url()
    if is_local:
        token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        await bot.send(
            f"{game_title} \n请复制地址到浏览器打开：\n{url}/waves/i/{token}\n您的id为【{ev.user_id}】\n登录地址10分钟内有效",
            at_sender=at_sender)
        # 手机登录
        data = {"mobile": -1, "code": -1, "user_id": ev.user_id}
        cache.set(token, data)
        async with timeout(600):
            while True:
                result = cache.get(token)
                if result is None:
                    return await bot.send("登录超时!", at_sender=at_sender)
                if result.get("mobile") != -1 and result.get("code") != -1:
                    text = f"{result['mobile']},{result['code']}"
                    cache.delete(token)
                    break
                await asyncio.sleep(1)

        return await code_login(bot, ev, text)
    else:
        auth = {"bot_id": ev.bot_id, "user_id": ev.user_id}
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(url + "/waves/token", json=auth,
                                      headers={"Content-Type": "application/json"})
                token = r.json().get("token", "")
            except Exception as e:
                token = ""
                logger.error(e)
            if not token:
                return await bot.send("登录服务请求失败! 请稍后再试", at_sender=at_sender)
            else:
                await bot.send(
                    f"{game_title} \n请复制地址到浏览器打开：\n{url}/waves/i/{token}\n您的id为【{ev.user_id}】\n登录地址10分钟内有效",
                    at_sender=at_sender)
            async with timeout(600):
                while True:
                    result = await client.post(url + f"/waves/get", json={"token": token})
                    if result.status_code == 200:
                        data = result.json()
                        if data.get("ck"):
                            waves_user = await add_cookie(ev, data['ck'])
                            if waves_user:
                                return await bot.send(f"{game_title} 鸣潮id:{waves_user.uid}登录成功!",
                                                      at_sender=at_sender)
                            else:
                                await bot.send(
                                    f"{game_title} 账号登录失败\n\n 验证码错误，请重新输入", at_sender=at_sender)

                    await asyncio.sleep(1)


async def code_login(bot: Bot, ev: Event, text: str):
    at_sender = True if ev.group_id else False
    game_title = "[鸣潮]"
    # 手机+验证码
    try:
        phone_number, code = text.split(",")
        if not is_valid_chinese_phone_number(phone_number):
            raise ValueError("Invalid phone number")
    except ValueError as _:
        return await bot.send(
            f"{game_title} 手机号+验证码登录失败\n\n请参照以下格式:\n{PREFIX}登录 手机号,验证码", at_sender=at_sender)

    result = await kuro_api.login(phone_number, code)
    if not isinstance(result, dict) or result.get('code') != 200 or result.get('data') is None:
        return await bot.send(result.get("msg", f"{game_title} 验证码登录失败\n", at_sender=at_sender))
    token = result.get('data', {}).get("token", '')
    waves_user = await add_cookie(ev, token)
    if waves_user:
        return await bot.send(f"{game_title} 鸣潮id:{waves_user.uid}登录成功!", at_sender=at_sender)
    else:
        return await bot.send(f"{game_title} 账号登录失败\n\n请参照以下格式:\n{PREFIX}登录 手机号,验证码",
                              at_sender=at_sender)


async def login_help():
    card_img = get_waves_bg(900, 800)
    card_draw = ImageDraw.Draw(card_img)

    card_draw.text((20, 50), "登录帮助", "white", waves_font_40, 'lm')
    text = [
        '1. 直接暴露服务器公网ip给用户（云服务器）',
        '   1.1 gscore控制台将HOST设置为 0.0.0.0',
        '   1.2 服务器开放gscore的端口，默认为8765（注意及时修改账号或者密码',
        '2. 使用自己的域名',
        '   2.1 在ww配置`鸣潮登录url`中填写自己的域名',
        '   2.2 在ww配置`强制【鸣潮登录url】为自己的域名`开关开启',
        '   2.3 注意：域名需要解析到bot服务器，请选用你了解的方式进行配置',
        '       http://域名',
        '       http://域名:port',
        '       https://域名',
        '       https://域名:port',
        '3. 家里云或者不想暴露公网ip',
        '   3.1 询要域名地址请加群: 929275476',
        '   3.2 在ww配置`鸣潮登录url`中填写提供的域名'
    ]
    for i, t in enumerate(text):
        card_draw.text((20, 100 + i * 50), t, "white", waves_font_25, 'lm')
    card_img = add_footer(card_img, 600, 20)
    return await convert_img(card_img)


async def add_cookie(ev, token) -> Union[WavesUser, None]:
    ck_res = await deal.add_cookie(ev, token)
    if "成功" in ck_res:
        user = await WavesUser.get_user_by_attr(ev.user_id, ev.bot_id, 'cookie', token)
        if user:
            await WavesBind.insert_waves_uid(ev.user_id, ev.bot_id, user.uid, ev.group_id, lenth_limit=9)
        return user
    return None


@app.get("/waves/i/{auth}")
async def waves_login_index(auth: str):
    temp = cache.get(auth)
    if temp is None:
        template = waves_templates.get_template("404.html")
        return HTMLResponse(template.render())
    else:
        url, _ = await get_url()
        template = waves_templates.get_template("index.html")
        return HTMLResponse(template.render(server_url=url, auth=auth, userId=temp.get('user_id', '')))


class LoginModel(BaseModel):
    auth: str
    mobile: str
    code: str


@app.post("/waves/login")
async def waves_login(data: LoginModel):
    temp = cache.get(data.auth)
    if temp is None:
        return {"success": False, "msg": "登录超时"}

    temp.update(data.dict())
    cache.set(data.auth, temp)
    return {"success": True}
