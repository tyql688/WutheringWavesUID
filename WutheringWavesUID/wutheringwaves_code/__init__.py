import json

import httpx

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..wutheringwaves_config import PREFIX

sv_waves_code = SV('鸣潮兑换码')

url = 'https://newsimg.5054399.com/comm/mlcxqcommon/static/wap/js/data_102.js'


@sv_waves_code.on_fullmatch((f'{PREFIX}code', f'{PREFIX}兑换码'))
async def get_sign_func(bot: Bot, ev: Event):
    code_list = await get_code_list()
    if not code_list:
        return await bot.send('[获取兑换码失败] 请稍后再试')

    msgs = []
    for code in code_list:
        is_fail = code.get("is_fail", '0')
        if is_fail == '1':
            continue
        order = code.get("order", '')
        reward = code.get("reward", '')
        label = code.get("label", '')
        msg = [
            f'兑换码: {order}',
            f'奖励: {reward}',
            label
        ]
        msgs.append('\n'.join(msg))

    await bot.send(msgs)


async def get_code_list():
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.get(url, timeout=10)
            json_data = res.text.split('=', 1)[1].strip().rstrip(';')
            return json.loads(json_data)
    except Exception as e:
        logger.exception('[获取兑换码失败] ', e)
        return
