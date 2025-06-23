from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils import hakush_api
from ..utils.limit_user_card import load_limit_user_card
from ..utils.resource.download_all_resource import download_all_resource

sv_download_config = SV("资源下载", pm=1)


@sv_download_config.on_fullmatch(("下载全部资源", "补充资源", "刷新补充资源"))
async def send_download_resource_msg(bot: Bot, ev: Event):
    await bot.send("[鸣潮] 正在开始下载~可能需要较久的时间!")
    await download_all_resource()

    if "补充" in ev.command:
        isForce = True if "刷新" in ev.command else False
        all_char = await hakush_api.get_all_character()
        await hakush_api.download_all_char_pic(all_char, isForce)

        all_weapon = await hakush_api.get_all_weapon()
        await hakush_api.download_all_weapon_pic(all_weapon, isForce)
    await bot.send("[鸣潮] 下载完成！")


async def startup():
    logger.info(
        "[鸣潮][资源文件下载] 正在检查与下载缺失的资源文件，可能需要较长时间，请稍等"
    )
    try:
        logger.info(f"[鸣潮][资源文件下载] {await download_all_resource()}")
    except Exception as e:
        logger.exception(e)

    try:
        logger.info(
            f"[鸣潮][加载角色极限面板] 数量: {len(await load_limit_user_card())}"
        )
    except Exception as e:
        logger.exception(e)
