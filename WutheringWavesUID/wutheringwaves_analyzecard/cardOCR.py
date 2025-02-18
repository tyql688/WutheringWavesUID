
# 标准库
import ssl
import asyncio
from pathlib import Path
import re

# 第三方库
import httpx
import easyocr
import numpy as np
from PIL import Image

# 项目内部模块
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.download_resource.download_file import download


SRC_PATH = Path(__file__).parent / "src"
CARD_PATH = Path(__file__).parent / "src/card.jpg"
CARD_NAME = "card.jpg"


async def async_ocr(bot: Bot, ev: Event):
    """
    异步OCR识别函数
    """
    await upload_discord_bot_card(bot, ev)
    ocr_results = await cut_card_ocr()

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

    logger.info(f"[鸣潮]卡片分析上传链接{upload_images}")
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

async def cut_card_ocr():
    """
    裁切卡片：角色，技能树*5，声骸*5，武器
        （按比例适配任意分辨率，1920*1080识别效果优良）
    """
    # 原始参考分辨率
    REF_WIDTH = 1072
    REF_HEIGHT = 602
    
    # 裁切区域比例（左、上、右、下），数字来自src/example_card_2.png
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
        # 根据相对比例计算实际裁切坐标
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
    async def card_part_ocr():
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
    ocr_results = await card_part_ocr()

    return ocr_results

async def ocr_results_to_dict(ocr_results):
    
    final_result = {
        "角色信息": {},
        "技能等级": [],
        "装备数据": [],
        "武器信息": {}
    }

    # 正则模式定义
    patterns = {
        "name": (re.compile(r'^[\u4e00-\u9fa5A-Za-z]+$'), 0.9),
        "level": (re.compile(r'LV\.?(\d+)'), 0.5),
        "player_id_en": (re.compile(r'PlayerID:(\w+)'), 0.8),
        "player_id_cn": (re.compile(r'玩家名稱\s*(\d+)'), 0.8),
        "uid": (re.compile(r'U[|]?D:(\d+)'), 0.8),
        "uid_cn": (re.compile(r'特徵碼\s*(\d+)'), 0.8),
        "skill_level": (re.compile(r'LV[./|](\d+)[^0-9]{0,2}10'), 0.4),
        "weapon_level": (re.compile(r'LV\.(\d+)'), 0.5),
        "numeric_value": (re.compile(r'(\d+\.?\d*%?)'), 0.3)
    }

    # 新增装备处理专用正则
    prop_pattern = re.compile(
        r'(\d+\.?\d*%?)(?!.*\d)',  # 匹配最后一个数值（解决跨行问题）
        re.IGNORECASE
    )
    attribute_aliases = {  # 属性名称标准化映射
        "Crit Rate": "暴击",
        "Crit DMG": "暴击伤害",
        "DMG Bonus": "伤害加成",
        # ...其他英文别名映射
    }

     # 处理角色信息 (image_0)
    if ocr_results:
        for data in ocr_results[0]:
            text, conf = data[1], data[2]
            
            # 匹配角色名
            if patterns["name"][0].fullmatch(text) and conf >= patterns["name"][1]:
                if '角色名' not in final_result["角色信息"]:
                    final_result["角色信息"]["角色名"] = text
            
            # 匹配等级
            level_match = patterns["level"][0].search(text)
            if level_match and conf >= patterns["level"][1]:
                if '等级' not in final_result["角色信息"]:
                    final_result["角色信息"]["等级"] = int(level_match.group(1))
            
            # 匹配英文UID
            uid_match = patterns["uid"][0].search(text)
            if uid_match and conf >= patterns["uid"][1]:
                final_result["角色信息"]["UID"] = uid_match.group(1)
            
            # 匹配中文UID
            uid_cn_match = patterns["uid_cn"][0].search(text)
            if uid_cn_match and conf >= patterns["uid_cn"][1]:
                final_result["角色信息"]["UID"] = uid_cn_match.group(1)

        # 处理技能等级 (image_1-5)
        for idx in range(1, 6):
            if idx >= len(ocr_results):
                continue
                
            max_level = 0
            for data in ocr_results[idx]:
                text, conf = data[1], data[2]
                match = patterns["skill_level"][0].search(text)
                if match and conf >= patterns["skill_level"][1]:
                    level = int(match.group(1))
                    if level > max_level:
                        max_level = level
            final_result["技能等级"].append(max_level if max_level else None)
            
        # 处理装备数据 (image_6-10)
        for idx in range(6, 11):
            if idx >= len(ocr_results):
                continue
                
            equipment = {
                "mainProps": [],
                "subProps": []
            }
            buffer = []
            current_attr = None
            
            for data in sorted(ocr_results[idx], key=lambda x: x[0][0][1]):  # 按Y坐标排序
                text, conf = data[1], data[2]
                
                # 数值提取和关联
                value_match = prop_pattern.search(text)
                if value_match and conf > 0.5:
                    value = value_match.group(1)
                    if current_attr:
                        buffer.append((current_attr, value))
                    current_attr = None
                else:
                    # 标准化属性名称
                    clean_attr = attribute_aliases.get(text, text)
                    clean_attr = re.sub(r'[+：]', '', clean_attr).strip()
                    current_attr = clean_attr if len(clean_attr) > 1 else None

            # 智能分配词条
            valid_entries = [entry for entry in buffer if is_valid_prop(entry)]
            
            # 主词条逻辑（取前两个有效词条）
            for entry in valid_entries[:2]:
                equipment["mainProps"].append({
                    "attributeName": entry[0],
                    "attributeValue": entry[1],
                    "iconUrl": "" 
                })
            
            # 副词条逻辑（取接下来5个有效词条）
            for entry in valid_entries[2:7]:
                equipment["subProps"].append({
                    "attributeName": entry[0],
                    "attributeValue": entry[1]
                })

            # 有效性验证
            if len(equipment["mainProps"]) >= 1 and len(equipment["subProps"]) >= 3:
                final_result["装备数据"].append(equipment)
        
        # 处理武器信息 (image_11)
        if len(ocr_results) > 11:
            weapon_info = ocr_results[11]
            weapon_name = ""
            max_conf = 0
            
            for data in weapon_info:
                text, conf = data[1], data[2]
                # 寻找置信度最高的非等级条目作为武器名
                if conf > max_conf and not patterns["weapon_level"][0].search(text):
                    weapon_name = text
                    max_conf = conf
                
                # 匹配武器等级
                level_match = patterns["weapon_level"][0].search(text)
                if level_match and conf >= patterns["weapon_level"][1]:
                    final_result["武器信息"]["等级"] = int(level_match.group(1))

            final_result["武器信息"]["名称"] = weapon_name
            final_result["武器信息"]["突破等级"] = "已突破" if any("突破等级" in data[1] for data in weapon_info) else "未突破"

    return final_result

def is_valid_prop(entry):
    """验证词条有效性"""
    name, value = entry
    # 排除无效属性
    if name in ["HP", "DEF", "ATK"] and not value.endswith('%'):
        return False
    # 数值范围验证
    try:
        num = float(value.replace('%', ''))
        if '%' in value:
            return 0 < num <= 100
        return 0 < num < 2000
    except:
        return False


if __name__ == "__main__":
    # 图片的绝对路径
    ocr_results = asyncio.run(cut_card_ocr())  # 运行异步函数
    # 打印识别结果
    for i, result in enumerate(ocr_results):
        for data in result:
            text, confidence = data[1], data[2]
            print(f"OCR Result for image_{i}: 置信度: {confidence:.2f}, 文本: {text}")

    final_result = asyncio.run(ocr_results_to_dict(ocr_results))
    print(final_result)