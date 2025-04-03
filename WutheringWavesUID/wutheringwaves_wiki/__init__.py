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

from ..utils.name_convert import alias_to_char_name, char_name_to_char_id
from ..utils.resource.RESOURCE_PATH import GUIDE_CONFIG_MAP
from ..wutheringwaves_config import WutheringWavesConfig
from .bilibili import GuideBilibili
from .draw_char import draw_char_wiki
from .draw_echo import draw_wiki_detail
from .draw_weapon import draw_wiki_weapon
from .main import Guide
from .tap import GuideTap

sv_waves_guide = SV("鸣潮攻略")
sv_waves_wiki = SV("鸣潮wiki")


@sv_waves_guide.on_regex(
    r"^[\u4e00-\u9fa5]+(?:共鸣链|命座|天赋|技能|图鉴|wiki|介绍)$", block=True
)
async def send_waves_wiki(bot: Bot, ev: Event):
    match = re.search(
        r"(?P<wiki_name>[\u4e00-\u9fa5]+)(?P<wiki_type>共鸣链|命座|天赋|技能|图鉴|wiki|介绍)",
        ev.raw_text,
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    wiki_name = ev.regex_dict.get("wiki_name", "")
    wiki_type = ev.regex_dict.get("wiki_type")

    at_sender = True if ev.group_id else False
    if wiki_type in ("共鸣链", "命座", "天赋", "技能"):
        char_name = wiki_name
        char_id = char_name_to_char_id(char_name)
        if not char_id:
            msg = f"[鸣潮] wiki【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)

        name = alias_to_char_name(char_name)
        if name == "漂泊者·衍射":
            name = "漂泊者-女-衍射"
        elif name == "漂泊者·湮灭":
            name = "漂泊者-女-湮灭"
        await bot.logger.info(f"[鸣潮] 开始获取{name}wiki")
        query_role_type = (
            "天赋" if "技能" in wiki_type or "天赋" in wiki_type else "命座"
        )
        img = await draw_char_wiki(char_id, query_role_type)
        if isinstance(img, str):
            msg = f"[鸣潮] wiki【{wiki_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)
        await bot.send(img)
    else:
        img = await draw_wiki_weapon(wiki_name)
        if isinstance(img, str) or not img:
            echo_name = wiki_name
            await bot.logger.info(f"[鸣潮] 开始获取{echo_name}wiki")
            img = await draw_wiki_detail("声骸", echo_name)

        if isinstance(img, str) or not img:
            msg = f"[鸣潮] wiki【{wiki_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)

        await bot.send(img)


@sv_waves_guide.on_regex(r"[\u4e00-\u9fa5]+攻略$", block=True)
async def send_role_guide_pic(bot: Bot, ev: Event):
    match = re.search(r"(?P<char>[\u4e00-\u9fa5]+)攻略", ev.raw_text)
    if not match:
        return
    ev.regex_dict = match.groupdict()

    char_name = ev.regex_dict.get("char", "")
    char_id = char_name_to_char_id(char_name)
    at_sender = True if ev.group_id else False
    if not char_id:
        msg = f"[鸣潮] 角色名【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        return await bot.send(msg, at_sender)

    name = alias_to_char_name(char_name)
    await bot.logger.info(f"[鸣潮] 开始获取{name}图鉴")

    config = WutheringWavesConfig.get_config("WavesGuideProvideNew")
    zip_list = []
    if config.data == "all":
        for i in config.options:
            if i == "all":
                continue
            name_path = GUIDE_CONFIG_MAP[i][0] / f"{name}.jpg"
            auth_id = GUIDE_CONFIG_MAP[i][1]
            source_type = GUIDE_CONFIG_MAP[i][2]
            zip_list.append((i, name_path, auth_id, source_type))
    else:
        if config.data in GUIDE_CONFIG_MAP:
            name_path = GUIDE_CONFIG_MAP[config.data][0] / f"{name}.jpg"
            auth_id = GUIDE_CONFIG_MAP[config.data][1]
            source_type = GUIDE_CONFIG_MAP[config.data][2]
            zip_list.append((config.data, name_path, auth_id, source_type))

    if not zip_list:
        msg = f"[鸣潮] 角色名{char_name}无法找到角色攻略图提供方, 请检查配置！\n"
        return await bot.send(msg, at_sender)

    imgs = []
    for auth_name, name_path, auth_id, source_type in zip_list:
        # if is_force or not name_dir.exists() or len(os.listdir(name_dir)) == 0:
        #     await download_guide_pic(auth_id, name, name_dir, is_force, source_type)
        imgs.extend(await process_images_new(auth_name, name_path))

    if len(imgs) == 0:
        msg = f"[鸣潮] 角色名【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        return await bot.send(msg, at_sender)

    return await send_images_based_on_config(config, imgs, bot)


async def send_images_based_on_config(config, imgs: list, bot: Bot):
    logger.debug(f"[鸣潮] 开始发送{config.data}攻略图片,长度为{len(imgs)}")
    # 处理发送逻辑
    # 裁切了 或者 all
    if config.data == "all" or len(imgs) > 2:
        await bot.send(imgs)
    # 只有一个攻略组，且没裁切
    elif len(imgs) == 2:
        await bot.send(imgs[1])
    else:
        await bot.send(imgs)


async def process_images_new(auth_name: str, _dir: Path):
    imgs = []
    try:
        from PIL import Image
        with Image.open(_dir) as img:
            width, height = img.size

            # 计算长宽比（纵边 / 横边）
            max_side = max(width, height)
            aspect_ratio = height / width

            # 定义裁切阈值
            CROP_ASPECT_RATIO = 5    # 长宽比超过 5 时裁切
            MAX_SINGLE_SIDE = 4000   # 单边最大允许像素（防止过大）

            # 判断是否需要裁切
            need_crop = False
            if aspect_ratio > CROP_ASPECT_RATIO:
                need_crop = True
                logger.info(f"长宽比 {aspect_ratio:.1f} 超过阈值 {CROP_ASPECT_RATIO}，启动裁切")
            elif max_side > MAX_SINGLE_SIDE:
                need_crop = True
                logger.info(f"单边尺寸 {max_side} 超过阈值 {MAX_SINGLE_SIDE}，启动裁切")

            if not need_crop:
                # 无需裁切，直接发送原图
                img_bytes = await convert_img(img, is_base64=True)
                imgs.append(img_bytes)
            else:
                # 裁切方向（纵向）
                segment_length = min(width * CROP_ASPECT_RATIO, MAX_SINGLE_SIDE)
                # 计算裁切的段数 
                # segments = math.ceil(height / segment_length)
                segments = (height + segment_length - 1) // segment_length

                # 均匀裁切图片
                for i in range(segments):
                    top = int(i * segment_length)
                    bottom = min(top + segment_length, height)
                    box = (0, top, width, bottom)

                    # 裁切并保存
                    cropped = img.crop(box)
                    img_bytes = await convert_img(cropped, is_base64=True)
                    imgs.append(img_bytes)

    except Exception as e:
        logger.warning(f"攻略图片读取失败 {_dir}: {e}")
    if len(imgs) > 0:
        imgs.insert(0, f"攻略作者：{auth_name}")
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
        imgs.insert(0, f"攻略作者：{auth_name}")
    return imgs


async def fetch_urls(auth_id, name, source_type) -> Union[List[str], None]:
    urls = None

    try:
        if source_type == "kuro":
            urls = await Guide().get(name, auth_id)
        elif source_type == "tap":
            urls = await GuideTap().get(name, auth_id)
        elif source_type == "bilibili":
            urls = await GuideBilibili().get(name, auth_id)
    except Exception:
        return None

    return urls if urls else None


async def download_guide_pic(
    auth_id: int, name: str, _dir: Path, is_force: bool, source_type: str
):
    urls = await fetch_urls(auth_id, name, source_type)
    if not urls:
        return
    if is_force:
        force_delete_dir(_dir)
    for index, url in enumerate(urls):
        _dir.mkdir(parents=True, exist_ok=True)
        await download(url, _dir, f"{name}_{index}.jpg", tag="[鸣潮]")


def force_delete_dir(_dir: Path):
    try:
        if _dir.exists() and _dir.is_dir():
            shutil.rmtree(_dir)
    except Exception as e:
        logger.exception(f"Error deleting directory {_dir}: {e}")
