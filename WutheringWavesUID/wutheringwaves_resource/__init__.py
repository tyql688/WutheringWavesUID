from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from ..utils import hakush_api
from ..utils.resource.download_all_resource import download_all_resource
from ..wutheringwaves_config import PREFIX

sv_download_config = SV('下载资源', pm=2)


@sv_download_config.on_fullmatch((f'{PREFIX}下载全部资源', f'{PREFIX}补充资源'))
async def send_download_resource_msg(bot: Bot, ev: Event):
    await bot.send('[鸣潮] 正在开始下载~可能需要较久的时间!')
    await download_all_resource()

    if '补充' in ev.command:
        all_char = await hakush_api.get_all_character()
        await hakush_api.download_all_avatar_pic(all_char)
        await hakush_api.download_all_pile_pic(all_char)

        all_weapon = await hakush_api.get_all_weapon()
        await hakush_api.download_all_weapon_pic(all_weapon)
    await bot.send('[鸣潮] 下载完成！')


async def startup():
    logger.info(
        '[鸣潮][资源文件下载] 正在检查与下载缺失的资源文件，可能需要较长时间，请稍等'
    )
    logger.info(f'[鸣潮][资源文件下载] {await download_all_resource()}')
