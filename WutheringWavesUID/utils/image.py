import os
import random
from io import BytesIO
from pathlib import Path
from typing import Union, Literal, Optional

from PIL import Image, ImageOps

from gsuid_core.models import Event
from gsuid_core.utils.image.image_tools import get_qq_avatar, crop_center_img
from gsuid_core.utils.image.utils import sget
from ..utils.resource.RESOURCE_PATH import (
    AVATAR_PATH,
    WEAPON_PATH,
    ROLE_PILE_PATH,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'
GREY = (216, 216, 216)
BLACK_G = (40, 40, 40)
YELLOW = (255, 200, 1)
RED = (255, 0, 0)
BLUE = (1, 183, 255)
GOLD = (224, 202, 146)
SPECIAL_GOLD = (234, 183, 4)

# 冷凝-凝夜白霜
WAVES_FREEZING = (53, 152, 219)
# 热熔-熔山裂谷
WAVES_MOLTEN = (186, 55, 42)
# 导电-彻空冥雷
WAVES_VOID = (185, 106, 217)
# 气动-啸谷长风
WAVES_SIERRA = (22, 145, 121)
# 衍射-浮星祛暗
WAVES_CELESTIAL = (241, 196, 15)
# 湮灭-沉日劫明
WAVES_SINKING = (132, 63, 161)
# 治疗-隐世回光
WAVES_REJUVENATING = (45, 194, 107)
# 辅助-轻云出月
WAVES_MOONLIT = (149, 165, 166)
# 攻击-不绝余音
WAVES_LINGERING = (52, 73, 94)

WAVES_ECHO_MAP = {
    "凝夜白霜": WAVES_FREEZING,
    "熔山裂谷": WAVES_MOLTEN,
    "彻空冥雷": WAVES_VOID,
    "啸谷长风": WAVES_SIERRA,
    "浮星祛暗": WAVES_CELESTIAL,
    "沉日劫明": WAVES_SINKING,
    "隐世回光": WAVES_REJUVENATING,
    "轻云出月": WAVES_MOONLIT,
    "不绝余音": WAVES_LINGERING,
}


async def get_random_waves_role_pile():
    path = random.choice(os.listdir(f'{ROLE_PILE_PATH}'))
    return Image.open(f'{ROLE_PILE_PATH}/{path}').convert('RGBA')


async def get_role_pile(resource_id: Union[int, str]) -> Image.Image:
    name = f"role_pile_{resource_id}.png"
    path = ROLE_PILE_PATH / name
    if path.exists():
        return Image.open(path).convert("RGBA")


async def get_square_avatar(resource_id: Union[int, str]) -> Image.Image:
    name = f"role_head_{resource_id}.png"
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


async def get_square_weapon(resource_id: Union[int, str]) -> Image.Image:
    name = f"weapon_{resource_id}.png"
    path = WEAPON_PATH / name
    if path.exists():
        return Image.open(path).convert("RGBA")


async def get_attribute(name: str = "", is_simple: bool = False) -> Image.Image:
    if is_simple:
        name = f'attribute/attr_simple_{name}.png'
    else:
        name = f'attribute/attr_{name}.png'
    return Image.open(TEXT_PATH / name).convert("RGBA")


async def get_attribute_prop(name: str = "") -> Image.Image:
    return Image.open(TEXT_PATH / f'attribute_prop/attr_prop_{name}.png').convert("RGBA")


async def get_attribute_effect(name: str = "") -> Image.Image:
    return Image.open(TEXT_PATH / f'attribute_effect/attr_{name}.webp').convert("RGBA")


async def get_weapon_type(name: str = "") -> Image.Image:
    return Image.open(TEXT_PATH / f'weapon_type/weapon_type_{name}.png').convert("RGBA")


def get_waves_bg(w: int, h: int, bg: str = 'bg') -> Image.Image:
    img = Image.open(TEXT_PATH / f'{bg}.jpg').convert('RGBA')
    return crop_center_img(img, w, h)


def get_crop_waves_bg(w: int, h: int, bg: str = 'bg') -> Image.Image:
    img = Image.open(TEXT_PATH / f'{bg}.jpg').convert('RGBA')

    width, height = img.size

    crop_box = (0, height // 2, width, height)

    cropped_image = img.crop(crop_box)

    return crop_center_img(cropped_image, w, h)


async def get_event_avatar(
    ev: Event, avatar_path: Optional[Path] = None, is_valid_at: bool = True
) -> Image.Image:
    img = None
    if ev.bot_id == 'onebot' and ev.at and is_valid_at:
        return await get_qq_avatar(ev.at)
    elif 'avatar' in ev.sender and ev.sender['avatar']:
        avatar_url = ev.sender['avatar']
        content = (await sget(avatar_url)).content
        return Image.open(BytesIO(content)).convert('RGBA')
    elif ev.bot_id == 'onebot' and not ev.sender:
        return await get_qq_avatar(ev.user_id)
    elif avatar_path:
        pic_path_list = list(avatar_path.iterdir())
        if pic_path_list:
            path = random.choice(pic_path_list)
            img = Image.open(path).convert('RGBA')

    if img is None:
        img = await get_square_avatar(1203)

    return img


def get_footer(color: Literal["white", "black"] = 'white'):
    return Image.open(TEXT_PATH / f'footer_{color}.png')


def add_footer(
    img: Image.Image,
    w: int = 0,
    offset_y: int = 0,
    is_invert: bool = False,
    color: Literal["white", "black"] = 'white'
):
    footer = get_footer(color)
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
