from gsuid_core.bot import Bot
from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.logger import logger

from .cardOCR import async_ocr


sv_discord_bot_card_analyze = SV(f"waves分析discord_bot卡片")


@sv_discord_bot_card_analyze.on_fullmatch(
    ("分析卡片", "卡片分析", "dc卡片", "识别卡片", "分析"), block=True
)
async def analyze_card(bot: Bot, ev: Event):
    """
    处理 Discord 上的图片分析请求。
    
    :param bot: Bot对象，用于发送消息。
    :param ev: 事件对象，包含用户信息和上传的图片信息。
    """

    resp = await bot.receive_resp(
        f'[鸣潮] 请在30秒内发送dc官方bot生成的卡片图或图片链接\n(分辨率尽可能为1920*1080，过低可能导致识别失败)',
    )
    if resp is not None:
        await async_ocr(bot, resp)