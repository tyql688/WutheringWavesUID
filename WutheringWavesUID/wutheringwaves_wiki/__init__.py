import os
import re
import shutil
from pathlib import Path
from typing import List, Union

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.download_resource.download_file import download
from gsuid_core.utils.image.convert import convert_img
from .bilibili import GuideBilibili
from .main import Guide
from .tap import GuideTap
from .wiki import draw_wiki_detail
from ..utils.name_convert import alias_to_char_name, char_name_to_char_id, alias_to_weapon_name
from ..utils.resource.RESOURCE_PATH import (
    GUIDE_CONFIG_MAP,
)
from ..wutheringwaves_config import WutheringWavesConfig, PREFIX

sv_waves_guide = SV('鸣潮攻略')
sv_waves_wiki = SV('鸣潮wiki')


@sv_waves_guide.on_regex(rf'^{PREFIX}[\u4e00-\u9fa5]+(?:共鸣链|命座|天赋|技能|图鉴|wiki|介绍)$', block=True)
async def send_waves_wiki(bot: Bot, ev: Event):
    match = re.search(
        rf'{PREFIX}(?P<wiki_name>[\u4e00-\u9fa5]+)(?P<wiki_type>共鸣链|命座|天赋|技能|图鉴|wiki|介绍)',
        ev.raw_text
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    wiki_name = ev.regex_dict.get("wiki_name")
    wiki_type = ev.regex_dict.get("wiki_type")

    at_sender = True if ev.group_id else False
    if wiki_type in ('共鸣链', '命座', '天赋', '技能'):
        char_name = wiki_name
        char_id = char_name_to_char_id(char_name)
        if not char_id:
            msg = f'[鸣潮] wiki【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n'
            return await bot.send(msg, at_sender)

        name = alias_to_char_name(char_name)
        if name == '漂泊者·衍射':
            name = '漂泊者-女-衍射'
        elif name == '漂泊者·湮灭':
            name = '漂泊者-女-湮灭'
        await bot.logger.info(f'[鸣潮] 开始获取{name}wiki')
        query_role_type = "天赋" if "技能" in wiki_type or "天赋" in wiki_type else "命座"
        img = await draw_wiki_detail("共鸣者", name, query_role_type)
        if isinstance(img, str):
            msg = f"[鸣潮] wiki【{wiki_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)
        await bot.send(img)
    else:

        weapon_name = alias_to_weapon_name(wiki_name)
        await bot.logger.info(f'[鸣潮] 开始获取{weapon_name}wiki')
        img = await draw_wiki_detail("武器", weapon_name)
        if isinstance(img, str):
            echo_name = wiki_name
            await bot.logger.info(f'[鸣潮] 开始获取{echo_name}wiki')
            img = await draw_wiki_detail("声骸", echo_name)

        if isinstance(img, str):
            msg = f"[鸣潮] wiki【{wiki_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)

        await bot.send(img)


@sv_waves_guide.on_regex(rf'^{PREFIX}[\u4e00-\u9fa5]+攻略$', block=True)
async def send_role_guide_pic(bot: Bot, ev: Event):
    match = re.search(
        rf'{PREFIX}(?P<char>[\u4e00-\u9fa5]+)攻略',
        ev.raw_text
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()

    char_name = ev.regex_dict.get("char")
    char_id = char_name_to_char_id(char_name)
    at_sender = True if ev.group_id else False
    if not char_id:
        msg = f'[鸣潮] 角色名【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n'
        return await bot.send(msg, at_sender)

    name = alias_to_char_name(char_name)
    await bot.logger.info(f'[鸣潮] 开始获取{name}图鉴')

    config = WutheringWavesConfig.get_config('WavesGuideProvide')
    zip_list = []
    if config.data == 'all':
        for i in config.options:
            if i == 'all':
                continue
            name_path = GUIDE_CONFIG_MAP[i][0] / f'{name}.jpg'
            auth_id = GUIDE_CONFIG_MAP[i][1]
            source_type = GUIDE_CONFIG_MAP[i][2]
            zip_list.append((i, name_path, auth_id, source_type))
    else:
        if config.data in GUIDE_CONFIG_MAP:
            name_path = GUIDE_CONFIG_MAP[config.data][0] / f'{name}.jpg'
            auth_id = GUIDE_CONFIG_MAP[config.data][1]
            source_type = GUIDE_CONFIG_MAP[config.data][2]
            zip_list.append((config.data, name_path, auth_id, source_type))

    if not zip_list:
        msg = f'[鸣潮] 角色名{char_name}无法找到角色攻略图提供方, 请检查配置！\n'
        return await bot.send(msg, at_sender)

    imgs = []
    for auth_name, name_path, auth_id, source_type in zip_list:
        # if is_force or not name_dir.exists() or len(os.listdir(name_dir)) == 0:
        #     await download_guide_pic(auth_id, name, name_dir, is_force, source_type)
        imgs.extend(await process_images_new(auth_name, name_path))

    if len(imgs) == 0:
        msg = f'[鸣潮] 角色名【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n'
        return await bot.send(msg, at_sender)

    return await send_images_based_on_config(config, imgs, bot)


async def send_images_based_on_config(config, imgs: list, bot: Bot):
    # 处理发送逻辑
    if config.data == 'all':
        await bot.send(imgs)
    elif len(imgs) == 2:
        await bot.send(imgs[1])
    else:
        await bot.send(imgs)


async def process_images_new(auth_name: str, _dir: Path):
    imgs = []
    try:
        img = await convert_img(_dir)
        imgs.append(img)
    except Exception as e:
        logger.warning(f"攻略图片读取失败 {_dir}: {e}")
    if len(imgs) > 0:
        imgs.insert(0, f'攻略作者：{auth_name}')
    return imgs


async def process_images(auth_name: str, _dir: Path):
    imgs = []
    if _dir.exists() and len(os.listdir(_dir)) > 0:
        path_list = sorted(os.listdir(_dir))
        for _path in path_list:
            try:
                img = await convert_img(_dir / _path)
                imgs.append(img)
            except Exception as e:
                logger.warning(f"攻略图片读取失败 {_path}: {e}")
    if len(imgs) > 0:
        imgs.insert(0, f'攻略作者：{auth_name}')
    return imgs


async def fetch_urls(auth_id, name, source_type) -> Union[List[str], None]:
    urls = None

    try:
        if source_type == 'kuro':
            urls = await Guide().get(name, auth_id)
        elif source_type == 'tap':
            urls = await GuideTap().get(name, auth_id)
        elif source_type == 'bilibili':
            urls = await GuideBilibili().get(name, auth_id)
    except Exception as e:
        return None

    return urls if urls else None


async def download_guide_pic(auth_id: int, name: str, _dir: Path, is_force: bool, source_type: str):
    urls = await fetch_urls(auth_id, name, source_type)
    if not urls:
        return
    if is_force:
        force_delete_dir(_dir)
    for index, url in enumerate(urls):
        _dir.mkdir(parents=True, exist_ok=True)
        await download(url, _dir, f'{name}_{index}.jpg', tag="[鸣潮]")


def force_delete_dir(_dir: Path):
    try:
        if _dir.exists() and _dir.is_dir():
            shutil.rmtree(_dir)
    except Exception as e:
        print(f"Error deleting directory {_dir}: {e}")
