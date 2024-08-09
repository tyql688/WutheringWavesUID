from pathlib import Path

from PIL import ImageFont

FONT_ORIGIN_PATH = Path(__file__).parent / 'waves_fonts.ttf'


def waves_font_origin(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_ORIGIN_PATH), size=size)


waves_font_12 = waves_font_origin(12)
waves_font_14 = waves_font_origin(14)
waves_font_15 = waves_font_origin(15)
waves_font_18 = waves_font_origin(18)
waves_font_20 = waves_font_origin(20)
waves_font_22 = waves_font_origin(22)
waves_font_23 = waves_font_origin(23)
waves_font_24 = waves_font_origin(24)
waves_font_25 = waves_font_origin(25)
waves_font_26 = waves_font_origin(26)
waves_font_28 = waves_font_origin(28)
waves_font_30 = waves_font_origin(30)
waves_font_32 = waves_font_origin(32)
waves_font_34 = waves_font_origin(34)
waves_font_36 = waves_font_origin(36)
waves_font_38 = waves_font_origin(38)
waves_font_40 = waves_font_origin(40)
waves_font_42 = waves_font_origin(42)
waves_font_44 = waves_font_origin(44)
waves_font_50 = waves_font_origin(50)
waves_font_58 = waves_font_origin(58)
waves_font_60 = waves_font_origin(60)
waves_font_62 = waves_font_origin(62)
waves_font_70 = waves_font_origin(70)
waves_font_84 = waves_font_origin(84)
