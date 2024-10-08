from PIL import Image
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.help.utils import register_help

from .get_help import ICON, get_help
from ..wutheringwaves_config import PREFIX

sv_waves_help = SV('waves帮助')


@sv_waves_help.on_fullmatch(f'{PREFIX}帮助')
async def send_help_img(bot: Bot, ev: Event):
    logger.info('开始执行[waves帮助]')
    await bot.send(await get_help())

register_help('WutheringWavesUID', f'{PREFIX}帮助', Image.open(ICON))
