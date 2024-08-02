from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .add_ck import add_cookie
from ..utils.waves_prefix import PREFIX

waves_add_ck = SV('waves添加ck')


@waves_add_ck.on_prefix((f'{PREFIX}添加CK', f'{PREFIX}添加ck'))
async def send_waves_add_ck_msg(bot: Bot, ev: Event):
    ck = ev.text.strip()
    await bot.send(await add_cookie(ev, ck))
