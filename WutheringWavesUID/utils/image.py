import os
import random
from pathlib import Path
from typing import Literal

from PIL import Image, ImageOps

from gsuid_core.utils.image.image_tools import crop_center_img

TEXT_PATH = Path(__file__).parent / 'texture2d'
GREY = (216, 216, 216)
BLACK_G = (40, 40, 40)
YELLOW = (255, 200, 1)
BLUE = (1, 183, 255)
GOLD = (224, 202, 146)


async def get_random_waves_role_pile():
    pic_path_list = os.listdir(f'{TEXT_PATH}/role_pile')
    if pic_path_list:
        path = random.choice(pic_path_list)
    else:
        path = 'role_pile_anke.png'
    return Image.open(TEXT_PATH / f'role_pile/{path}').convert('RGBA')


async def get_role_head(name: str):
    return Image.open(TEXT_PATH / f'role_head/role_head_{name}.png').convert('RGBA')


async def get_weapon(name: str):
    return Image.open(TEXT_PATH / f'weapon/weapon_{name}.png').convert('RGBA')


def get_waves_bg(w: int, h: int, bg: str = 'bg') -> Image.Image:
    img = Image.open(TEXT_PATH / f'{bg}.jpg').convert('RGBA')
    return crop_center_img(img, w, h)


def add_footer(
    img: Image.Image,
    w: int = 0,
    offset_y: int = 0,
    is_invert: bool = False,
    color: Literal["white", "black"] = 'white'
):
    footer = Image.open(TEXT_PATH / f'footer_{color}.png')
    if is_invert:
        r, g, b, a = footer.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        rgb_image = ImageOps.invert(rgb_image.convert('RGB'))
        r2, g2, b2 = rgb_image.split()
        footer = Image.merge('RGBA', (r2, g2, b2, a))

    if w != 0:
        footer = footer.resize(
            (w, int(footer.size[1] * w / footer.size[0])),
        )

    x, y = (
        int((img.size[0] - footer.size[0]) / 2),
        img.size[1] - footer.size[1] - 20 + offset_y,
    )

    img.paste(footer, (x, y), footer)
    return img
