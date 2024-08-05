from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from .add_ck import add_cookie, add_tap
from ..utils.waves_prefix import PREFIX

waves_add_ck = SV('waves添加ck')
waves_bind_tap = SV('绑定tap')


@waves_add_ck.on_prefix((f'{PREFIX}添加CK', f'{PREFIX}添加ck'))
async def send_waves_add_ck_msg(bot: Bot, ev: Event):
    ck = ev.text.strip()
    await bot.send(await add_cookie(ev, ck))


@waves_bind_tap.on_prefix(
    (
            f'{PREFIX}绑定tap',
            f'{PREFIX}绑定taptap',
            f'{PREFIX}绑定TapTap',
            f'{PREFIX}绑定Tap',
            f'{PREFIX}绑定TAPTAP'
    )
)
async def send_waves_add_ck_msg(bot: Bot, ev: Event):
    tap_uid = ev.text.strip()
    await bot.send(await add_tap(ev, tap_uid))
