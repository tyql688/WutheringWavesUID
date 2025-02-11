
from gsuid_core.bot import Bot
from gsuid_core.sv import SL, SV
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.download_resource.download_file import download
from PIL import Image

import asyncio
import ssl
import time
import httpx
import easyocr
import numpy as np


import os
import random
from io import BytesIO
from pathlib import Path
from typing import Union, Literal, Optional, Tuple

from PIL import Image, ImageOps, ImageDraw, ImageFont

from gsuid_core.utils.image.image_tools import crop_center_img
from gsuid_core.utils.image.utils import sget


SRC_PATH = Path(__file__).parent / "src"
CARD_PATH = Path(__file__).parent / "src/card.jpg"
CARD_NAME = "card.jpg"


async def async_ocr(bot: Bot, ev: Event):
    """
    异步OCR识别函数
    """
    await upload_discord_bot_card(bot, ev)
    await cut_card()

async def get_image(ev: Event):
    """
    获取图片链接
    change from .upload_card.get_image
    """
    res = []
    for content in ev.content:
        if content.type == "img" and content.data and isinstance(content.data, str) and content.data.startswith("http"):
            res.append(content.data)
        elif content.type == "image" and content.data and isinstance(content.data, str) and content.data.startswith("http"):
            res.append(content.data)

    if not res and ev.image:
        res.append(ev.image)

    return res

async def upload_discord_bot_card(bot: Bot, ev: Event):
    """
    上传Discord机器人的卡片
    change from .upload_card.upload_custom_card
    """
    at_sender = True if ev.group_id else False

    upload_images = await get_image(ev)
    if not upload_images:
        return await bot.send(
            f"[鸣潮] 上传bot卡片失败\n", at_sender
        )

    success = True
    for upload_image in upload_images:
        # name = f"card_{int(time.time() * 1000)}.jpg"
        name = CARD_NAME
        if not CARD_PATH.exists():
            try:
                if httpx.__version__ >= "0.28.0":
                    ssl_context = ssl.create_default_context()
                    # ssl_context.set_ciphers("AES128-GCM-SHA256")
                    ssl_context.set_ciphers("DEFAULT")
                    sess = httpx.AsyncClient(verify=ssl_context)
                else:
                    sess = httpx.AsyncClient()
            except Exception as e:
                logger.exception(f"{httpx.__version__} - {e}")
                sess = None
            code = await download(upload_image, SRC_PATH, name, tag="[鸣潮]", sess=sess)
            if not isinstance(code, int) or code != 200:
                # 成功
                success = False
                break

    if success:
        return await bot.send(f"[鸣潮]上传卡片图成功！\n", at_sender)
    else:
        return await bot.send(f"[鸣潮]上传卡片图失败！\n", at_sender)

async def cut_card():
    """
    裁切卡片：角色，技能树*5，声骸*5，武器（按比例适配任意分辨率）
    """
    # 原始参考分辨率
    REF_WIDTH = 1072
    REF_HEIGHT = 602
    
    # 裁切区域比例（左、上、右、下）
    crop_ratios = [
        (  0/REF_WIDTH,   0/REF_HEIGHT, 420/REF_WIDTH, 350/REF_HEIGHT), # 角色
        (583/REF_WIDTH,  30/REF_HEIGHT, 653/REF_WIDTH, 130/REF_HEIGHT), # 技能树1
        (456/REF_WIDTH, 115/REF_HEIGHT, 526/REF_WIDTH, 215/REF_HEIGHT), # 技能树2
        (694/REF_WIDTH, 115/REF_HEIGHT, 764/REF_WIDTH, 215/REF_HEIGHT), # 技能树3
        (501/REF_WIDTH, 250/REF_HEIGHT, 571/REF_WIDTH, 350/REF_HEIGHT), # 技能树4
        (650/REF_WIDTH, 250/REF_HEIGHT, 720/REF_WIDTH, 350/REF_HEIGHT), # 技能树5
        ( 10/REF_WIDTH, 350/REF_HEIGHT, 220/REF_WIDTH, 590/REF_HEIGHT), # 声骸1
        (220/REF_WIDTH, 350/REF_HEIGHT, 430/REF_WIDTH, 590/REF_HEIGHT), # 声骸2
        (430/REF_WIDTH, 350/REF_HEIGHT, 640/REF_WIDTH, 590/REF_HEIGHT), # 声骸3
        (640/REF_WIDTH, 350/REF_HEIGHT, 850/REF_WIDTH, 590/REF_HEIGHT), # 声骸4
        (850/REF_WIDTH, 350/REF_HEIGHT, 1060/REF_WIDTH, 590/REF_HEIGHT), # 声骸5
        (800/REF_WIDTH, 240/REF_HEIGHT, 1020/REF_WIDTH, 350/REF_HEIGHT), # 武器
    ]

    # 打开图片
    image = Image.open(CARD_PATH).convert('RGB')
    img_width, img_height = image.size  # 获取实际分辨率
    
    # 裁切图片
    cropped_images = []
    for i, ratio in enumerate(crop_ratios):
        # 计算实际裁切坐标
        left = ratio[0] * img_width
        top = ratio[1] * img_height
        right = ratio[2] * img_width
        bottom = ratio[3] * img_height
        
        # 四舍五入取整并确保不越界
        left = max(0, int(round(left)))
        top = max(0, int(round(top)))
        right = min(img_width, int(round(right)))
        bottom = min(img_height, int(round(bottom)))
        
        # 执行裁切
        cropped_image = image.crop((left, top, right, bottom))
        cropped_images.append(cropped_image)
        
        # 保存裁切后的图片
        cropped_image.save(f"{SRC_PATH}/_{i}.png")


    def card_part_ocr():
        """
        识别碎块图片
        """
        reader = easyocr.Reader(['ch_tra', 'en'])  # 选择语言，繁体中文和英语
        results = []
        for cropped_image in cropped_images:
            image_np = np.array(cropped_image) # 将PIL.Image转为numpy数组
            result = reader.readtext(image_np)
            results.append(result)
        return results


    # 调用 card_part_ocr 函数并获取识别结果
    ocr_results = card_part_ocr()

    # 打印识别结果
    for i, result in enumerate(ocr_results):
        for data in result:
            text, confidence = data[1], data[2]
            print(f"OCR Result for image_{i}: 置信度: {confidence:.2f}, 文本: {text}")

    return cropped_images




if __name__ == "__main__":
    # 图片的绝对路径
    asyncio.run(cut_card())  # 运行异步函数