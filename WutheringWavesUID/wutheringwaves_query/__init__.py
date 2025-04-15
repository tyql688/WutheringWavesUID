from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from .draw_char_hold_rate import get_char_hold_rate_img

sv_char_hold_rate = SV("waves角色持有率")


# 角色持有率指令
@sv_char_hold_rate.on_command(
    (
        "角色持有率",
        "角色持有率列表",
        "持有率",
        "群角色持有率",
        "群角色持有率列表",
        "群持有率",
    )
)
async def handle_char_hold_rate(bot: Bot, ev: Event):
    if "群" in ev.command:
        if not ev.group_id:
            return await bot.send("请在群聊中使用")
        img = await get_char_hold_rate_img(ev.group_id)
    else:
        img = await get_char_hold_rate_img()
    await bot.send(img)
