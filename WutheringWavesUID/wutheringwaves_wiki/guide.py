import re
from pathlib import Path

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.name_convert import alias_to_char_name
from ..utils.resource.RESOURCE_PATH import GUIDE_PATH
from ..wutheringwaves_config.wutheringwaves_config import WutheringWavesConfig

guide_map = {
    "金铃子攻略组": "JinLingZi",
    "結星": "JieXing",
    "Moealkyne": "Moealkyne",
    "小沐XMu": "XMu",
    "小羊早睡不遭罪": "XiaoYang",
}

guide_author_map = {v: k for k, v in guide_map.items()}


async def get_guide(bot: Bot, ev: Event, char_name: str):
    char_name = alias_to_char_name(char_name)
    logger.info(f"[鸣潮] 开始获取{char_name}图鉴")

    config = WutheringWavesConfig.get_config("WavesGuide").data

    imgs_result = []
    pattern = re.compile(re.escape(char_name), re.IGNORECASE)
    if "all" in config:
        for guide_path in GUIDE_PATH.iterdir():
            imgs = await get_guide_pic(
                guide_path,
                pattern,
                guide_author_map.get(guide_path.name, guide_path.name),
            )
            if len(imgs) == 0:
                continue
            imgs_result.extend(imgs)
    else:
        for guide_name in config:
            if guide_name in guide_map:
                guide_path = GUIDE_PATH / guide_map[guide_name]
            else:
                guide_path = GUIDE_PATH / guide_name

            imgs = await get_guide_pic(
                guide_path,
                pattern,
                guide_author_map.get(guide_path.name, guide_path.name),
            )
            if len(imgs) == 0:
                continue
            imgs_result.extend(imgs)

    if len(imgs_result) == 0:
        msg = f"[鸣潮] 角色名【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        return await bot.send(msg)

    await send_guide(config, imgs_result, bot)


async def get_guide_pic(guide_path: Path, pattern: re.Pattern, guide_author: str):
    imgs = []
    if not guide_path.is_dir():
        logger.warning(f"[鸣潮] 攻略路径错误 {guide_path}")
        return imgs

    if not guide_path.exists():
        logger.warning(f"[鸣潮] 攻略路径不存在 {guide_path}")
        return imgs

    for file in guide_path.iterdir():
        if not pattern.search(file.name):
            continue
        imgs.extend(await process_images_new(file))

    if len(imgs) > 0:
        imgs.insert(0, f"攻略作者：{guide_author}")

    return imgs


async def process_images_new(_dir: Path):
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
    return imgs


async def send_guide(config, imgs: list, bot: Bot):
    # 处理发送逻辑
    # 裁切了 或者 all
    if config.data == "all" or len(imgs) > 2:
        await bot.send(imgs)
    elif len(imgs) == 2:
        await bot.send(imgs[1])
    else:
        await bot.send(imgs)
