import os
import random
from pathlib import Path
from typing import Literal

from PIL import Image, ImageOps

from gsuid_core.utils.image.image_tools import crop_center_img
from ..utils.resource.RESOURCE_PATH import AVATAR_PATH, WEAPON_PATH

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


async def get_square_avatar(char_name: str = "") -> Image.Image:
    name = f"role_head_{char_name}.png"
    path = AVATAR_PATH / name
    if path.exists():
        return Image.open(path).convert("RGBA")


async def cropped_square_avatar(item_icon: Image.Image, size: int) -> Image.Image:
    # 目标尺寸
    target_width, target_height = size, size
    # 原始尺寸
    original_width, original_height = item_icon.size

    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    scale_ratio = max(width_ratio, height_ratio)
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)
    resized_image = item_icon.resize((new_width, new_height), Image.Resampling.LANCZOS)
    x_center = new_width // 2
    y_center = new_height // 2
    crop_area = (x_center - target_width // 2, y_center - target_height // 2,
                 x_center + target_width // 2, y_center + target_height // 2)
    resized_image = resized_image.crop(crop_area).convert('RGBA')
    return resized_image


async def get_square_weapon(char_name: str = "") -> Image.Image:
    name = f"weapon_{char_name}.png"
    path = WEAPON_PATH / name
    if path.exists():
        return Image.open(path).convert("RGBA")


async def get_attribute(name: str = "") -> Image.Image:
    return Image.open(TEXT_PATH / f'attribute/attr_{name}.png').convert("RGBA")


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
