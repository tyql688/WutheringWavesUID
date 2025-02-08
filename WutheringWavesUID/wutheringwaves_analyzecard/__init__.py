
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
 # 假设这是处理图片的函数

sv_discord_bot_card_analyze = SV(f"discord_bot卡片分析")


@sv_discord_bot_card_analyze.on_fullmatch(
    (
        f"分析卡片",
        f"卡片分析",
        f"dc卡片",
        f"识别卡片",
        f"分析",
    )
)
async def analyze_card(bot: Bot, ev: Event):
    """
    处理 Discord 上的图片分析请求。
    
    :param bot: Bot对象，用于发送消息。
    :param ev: 事件对象，包含用户信息和上传的图片信息。
    """
    
    await bot.send(f"[鸣潮] 获取成功")
    
