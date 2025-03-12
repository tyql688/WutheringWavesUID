from gsuid_core.bot import Bot
from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.logger import logger

from .cardOCR import async_ocr
from .changeEcho import change_echo
import re


waves_discord_bot_card_analyze = SV(f"waves分析discord_bot卡片")
waves_change_sonata_and_first_echo = SV(f"waves修改首位声骸与套装")


@waves_discord_bot_card_analyze.on_fullmatch(
    ("分析卡片", "卡片分析", "dc卡片", "fx", "分析"), block=True
)
async def analyze_card(bot: Bot, ev: Event):
    """处理 Discord 上的图片分析请求。"""

    resp = await bot.receive_resp(
        f'[鸣潮] 请在30秒内发送dc官方bot生成的卡片图或图片链接\n(分辨率尽可能为1920*1080，过低可能导致识别失败)',
    )
    if resp is not None:
        await async_ocr(bot, resp)

@waves_change_sonata_and_first_echo.on_regex(
    r"^改(?P<char>[\u4e00-\u9fa5]+?)(套装(?P<sonata>[\u4e00-\u9fa5]+?))?(声骸(?P<echo>[\u4e00-\u9fa5]+?))?$",
    block=True,
)
async def change_sonata_and_first_echo(bot: Bot, ev: Event):
    """处理国际服本地识别结果的声骸相关"""
    match = re.search(
        r"^.*改(?P<char>[\u4e00-\u9fa5]+?)(套装(?P<sonata>[\u4e00-\u9fa5]+?))?(声骸(?P<echo>[\u4e00-\u9fa5]+?))?$",
        ev.raw_text,
    )

    if not match:
        return
    ev.regex_dict = match.groupdict()

    await change_echo(bot, ev)