
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
    裁切卡片：角色，技能树*5，声骸*5，武器
    """
    # 裁切区域（左上角x坐标，左上角y坐标，右下角x坐标，右下角y坐标）
    crop_boxes = [
        (  0,   0, 420, 350),  # 角色
        (580,  30, 650, 130),  # 技能树1
        (460, 115, 530, 215),  # 技能树2
        (700, 115, 770, 215),  # 技能树3
        (500, 250, 570, 350),  # 技能树4
        (650, 250, 720, 350),  # 技能树5
        ( 10, 350, 220, 590),  # 声骸1
        (220, 350, 430, 590),  # 声骸2
        (430, 350, 640, 590),  # 声骸3
        (640, 350, 850, 590),  # 声骸4
        (850, 350, 1060, 590),  # 声骸5
        (800, 240, 1020, 350),  # 武器
    ]

     # 打开图片
    image = Image.open(CARD_PATH)
    
    # 裁切图片
    cropped_images = []
    for i, box in enumerate(crop_boxes):
        left, top, right, bottom = box
        cropped_image = image.crop((left, top, right, bottom))
        cropped_images.append(cropped_image)
        
        # 保存裁切后的图片
        cropped_image.save(f"{SRC_PATH}/_{i}.png")
    

    def card_part_ocr():
        """
        识别碎块图片
        """
        
        return 0


    return cropped_images




if __name__ == "__main__":
    # 图片的绝对路径
    image_path = Path(__file__).parent / "src/jinxi_card.png"
    print("图片路径:", image_path)
    asyncio.run(cut_card())  # 运行异步函数
    try:
        image = Image.open(image_path)  # 打开图片
        print("图片加载成功:", image)
        # 这里可以添加 OCR 识别代码
    except FileNotFoundError as e:
        print("文件未找到:", e)
    except Exception as e:
        print("发生错误:", e)